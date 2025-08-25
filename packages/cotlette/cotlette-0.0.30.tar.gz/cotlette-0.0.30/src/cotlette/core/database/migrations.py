from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
import uuid
from datetime import datetime


class MigrationManager:
    """
    Менеджер миграций для Cotlette ORM с использованием Alembic.
    """
    
    def __init__(self, database_url: str = None, migrations_dir: str = "migrations"):
        """
        Инициализация менеджера миграций.
        
        :param database_url: URL базы данных
        :param migrations_dir: Директория для миграций
        """
        if database_url is None:
            database_url = "sqlite:///db.sqlite3"
        
        self.database_url = database_url
        self.migrations_dir = Path(migrations_dir)
        self.alembic_cfg = None
        self._setup_alembic()
    
    def _setup_alembic(self):
        """Настройка Alembic конфигурации."""
        # Создаем директорию для миграций если её нет
        self.migrations_dir.mkdir(exist_ok=True)
        
        # Создаем директорию versions если её нет
        versions_dir = self.migrations_dir / "versions"
        versions_dir.mkdir(exist_ok=True)
        
        # Создаем alembic.ini если его нет
        alembic_ini_path = Path("alembic.ini")
        if not alembic_ini_path.exists():
            self._create_alembic_ini()
        
        # Создаем env.py если его нет
        env_py_path = self.migrations_dir / "env.py"
        if not env_py_path.exists():
            self._create_env_py()
        
        # Создаем script.py.mako если его нет
        script_py_mako_path = self.migrations_dir / "script.py.mako"
        if not script_py_mako_path.exists():
            self._create_script_py_mako()
        
        # Настраиваем конфигурацию Alembic
        self.alembic_cfg = Config("alembic.ini")
        self.alembic_cfg.set_main_option("script_location", str(self.migrations_dir))
        self.alembic_cfg.set_main_option("sqlalchemy.url", self.database_url)
    
    def _create_alembic_ini(self):
        """Создает файл alembic.ini."""
        ini_content = """[alembic]
script_location = migrations
sqlalchemy.url = sqlite:///db.sqlite3

# version number format
version_num_format = {0:04d}

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = ERROR
handlers = console
qualname =

[logger_sqlalchemy]
level = ERROR
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = ERROR
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = {levelname}-5.5s [{name}] {message}
datefmt = {H}:{M}:{S}
"""
        with open("alembic.ini", "w") as f:
            f.write(ini_content)
    
    def _create_env_py(self):
        """Создает файл env.py для Alembic."""
        env_content = '''from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from cotlette.core.database.sqlalchemy import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''
        with open(self.migrations_dir / "env.py", "w") as f:
            f.write(env_content)
    
    def _create_script_py_mako(self):
        """Создает файл script.py.mako для Alembic."""
        mako_content = '''"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade():
    ${upgrades if upgrades else "pass"}


def downgrade():
    ${downgrades if downgrades else "pass"}
'''
        with open(self.migrations_dir / "script.py.mako", "w") as f:
            f.write(mako_content)
    
    def init(self):
        """Инициализирует систему миграций."""
        if self.alembic_cfg is None:
            self._setup_alembic()
        
        try:
            command.init(self.alembic_cfg, str(self.migrations_dir))
        except Exception as e:
            # Если директория уже инициализирована, игнорируем ошибку
            if "already exists" not in str(e):
                raise
    
    def create_migration(self, message: str, models: List[Any] = None):
        """
        Создает новую миграцию.
        
        :param message: Сообщение для миграции
        :param models: Список моделей для миграции
        :return: Результат создания миграции
        """
        if self.alembic_cfg is None:
            self._setup_alembic()
        
        # Создаем SQL миграцию в файле
        if models:
            migration_content = self._generate_migration_content(models, message)
            # Создаем файл миграции
            migration_file = self._create_migration_file(migration_content, message)
            return migration_file
        
        # Создаем пустую миграцию для Alembic
        result = command.revision(self.alembic_cfg, message=message, autogenerate=False)
        return result
    
    def _generate_migration_content(self, models, message):
        """
        Генерирует содержимое миграции.
        """
        migration_sql = []
        
        for model in models:
            sql = self._create_table_sql(model)
            if sql:
                migration_sql.append(sql)
        
        return migration_sql
    
    def _create_migration_file(self, migration_content, message):
        """
        Создает файл миграции с SQL командами.
        """
        
        # Создаем уникальный ID для миграции (без дефисов)
        migration_id = str(uuid.uuid4()).replace('-', '')[:12]
        
        # Создаем SQL команды для upgrade
        upgrade_commands = []
        for sql in migration_content:
            upgrade_commands.append(f"    op.execute('''{sql}''')")
        
        # Создаем SQL команды для downgrade
        downgrade_commands = []
        for sql in migration_content:
            table_name = sql.split()[5]  # Получаем имя таблицы из CREATE TABLE
            downgrade_commands.append(f"    op.execute('DROP TABLE IF EXISTS {table_name}')")
        
        # Создаем содержимое файла миграции
        file_content = f'''"""Migration: {message}

Revision ID: {migration_id}
Revises: 
Create Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '{migration_id}'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Apply migration."""
    # ### commands auto generated by Cotlette ###
{chr(10).join(upgrade_commands)}
    # ### end Cotlette commands ###


def downgrade():
    """Revert migration."""
    # ### commands auto generated by Cotlette ###
{chr(10).join(downgrade_commands)}
    # ### end Cotlette commands ###
'''
        
        # Создаем файл миграции
        versions_dir = Path('migrations/versions')
        versions_dir.mkdir(exist_ok=True)
        
        migration_file = versions_dir / f"{migration_id}_.py"
        with open(migration_file, 'w') as f:
            f.write(file_content)
        
        return str(migration_file)
    
    def _create_table_sql(self, model):
        """
        Создает SQL для создания таблицы модели.
        """
        table_name = model.get_table_name()
        columns = []
        
        for field_name, field in model._fields.items():
            # Определяем тип колонки
            if field.column_type == int:
                column_type = "INTEGER"
            elif field.column_type == str:
                column_type = "TEXT"
            elif field.column_type == bool:
                column_type = "BOOLEAN"
            elif field.column_type == float:
                column_type = "REAL"
            else:
                column_type = "TEXT"
            
            # Добавляем ограничения
            constraints = []
            if field.primary_key:
                constraints.append("PRIMARY KEY")
            if field.unique:
                constraints.append("UNIQUE")
            if not field.primary_key:
                constraints.append("NOT NULL")
            
            column_def = f'"{field_name}" {column_type}'
            if constraints:
                column_def += f" {' '.join(constraints)}"
            
            columns.append(column_def)
        
        if columns:
            sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
            return sql
        
        return None
    
    def upgrade(self, revision: str = "head"):
        """
        Применяет миграции.
        
        :param revision: Ревизия для применения (по умолчанию "head")
        """
        if self.alembic_cfg is None:
            self._setup_alembic()
        
        command.upgrade(self.alembic_cfg, revision)
    
    def downgrade(self, revision: str):
        """
        Откатывает миграции.
        
        :param revision: Ревизия для отката
        """
        if self.alembic_cfg is None:
            self._setup_alembic()
        
        command.downgrade(self.alembic_cfg, revision)
    
    def current(self):
        """
        Возвращает текущую ревизию.
        """
        if self.alembic_cfg is None:
            self._setup_alembic()
        
        try:
            return command.current(self.alembic_cfg)
        except Exception:
            return None
    
    def history(self):
        """
        Возвращает историю миграций.
        """
        if self.alembic_cfg is None:
            self._setup_alembic()
        
        return command.history(self.alembic_cfg)
    
    def show(self, revision: str):
        """
        Показывает информацию о ревизии.
        
        :param revision: Ревизия для показа
        """
        if self.alembic_cfg is None:
            self._setup_alembic()
        
        return command.show(self.alembic_cfg, revision)
    
    def stamp(self, revision: str):
        """
        Отмечает текущую ревизию без применения миграций.
        
        :param revision: Ревизия для отметки
        """
        if self.alembic_cfg is None:
            self._setup_alembic()
        
        command.stamp(self.alembic_cfg, revision)


# Глобальный экземпляр менеджера миграций
migration_manager = MigrationManager() 