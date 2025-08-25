from cotlette.core.management.base import BaseCommand
from cotlette.core.database.migrations import migration_manager
from cotlette.core.database.models import ModelMeta
from cotlette.core.database.sqlalchemy import db
import sys
import os
from pathlib import Path
import glob


class Command(BaseCommand):
    help = "Создает новые миграции для моделей"

    def add_arguments(self, parser):
        parser.add_argument(
            '--message', '-m',
            type=str,
            help='Сообщение для миграции'
        )
        parser.add_argument(
            '--empty',
            action='store_true',
            help='Создать пустую миграцию'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показать что будет создано без создания миграции'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Принудительно создать миграцию даже если изменений нет'
        )

    def handle(self, *args, **options):
        message = options.get('message', 'Auto-generated migration')
        empty = options.get('empty', False)
        dry_run = options.get('dry_run', False)
        force = options.get('force', False)
        
        try:
            # Импортируем все модели для регистрации
            self._import_all_models()
            
            # Инициализируем систему миграций если нужно
            migration_manager.init()
            
            # Инициализируем базу данных если нужно
            if hasattr(db, 'initialize') and not db._initialized:
                db.initialize()
            
            # Получаем все зарегистрированные модели
            models = list(ModelMeta._registry.values())
            
            # Показываем информацию о найденных моделях
            self.stdout.write(
                self.style.SUCCESS(f'Найдено моделей: {len(models)}')
            )
            
            if models:
                self.stdout.write('Зарегистрированные модели:')
                for model in models:
                    self.stdout.write(f'  - {model.__name__} ({model.get_table_name()})')
            else:
                self.stdout.write('  (нет зарегистрированных моделей)')
            
            if not models and not empty:
                if dry_run:
                    self.stdout.write(
                        self.style.WARNING('Нет моделей для создания миграций')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING('Нет моделей для создания миграций. Используйте --empty для создания пустой миграции.')
                    )
                return
            
            # Проверяем, какие таблицы уже существуют в базе данных
            existing_tables = self._get_existing_tables()
            self.stdout.write(f'Существующие таблицы в БД: {len(existing_tables)}')
            if existing_tables:
                self.stdout.write('  - ' + '\n  - '.join(existing_tables))
            
            # Определяем, какие таблицы нужно создать
            tables_to_create = []
            for model in models:
                table_name = model.get_table_name()
                if table_name not in existing_tables:
                    tables_to_create.append(model)
            
            self.stdout.write(f'Таблиц для создания: {len(tables_to_create)}')
            if tables_to_create:
                self.stdout.write('  - ' + '\n  - '.join([model.get_table_name() for model in tables_to_create]))
            
            if not tables_to_create and not empty and not force:
                if dry_run:
                    self.stdout.write(
                        self.style.SUCCESS('Все таблицы уже существуют в базе данных')
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS('Все таблицы уже существуют в базе данных. Миграция не создана.')
                    )
                return
            
            if dry_run:
                self.stdout.write(
                    self.style.SUCCESS(f'Будет создана миграция: {message}')
                )
                if tables_to_create:
                    self.stdout.write('Изменения:')
                    for model in tables_to_create:
                        self.stdout.write(f'  - Создание таблицы: {model.get_table_name()}')
                elif empty:
                    self.stdout.write('  - Пустая миграция')
                return
            
            # Создаем миграцию
            if empty:
                result = migration_manager.create_migration(message, [])
            else:
                result = migration_manager.create_migration(message, tables_to_create)
            
            if result:
                # Проверяем, не пустая ли миграция (только если не --empty)
                if not empty and self._is_migration_empty(result):
                    self.stdout.write(
                        self.style.WARNING('Миграция не создана (нет изменений)')
                    )
                    # Удаляем пустую миграцию
                    self._remove_empty_migration(result)
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f'Миграция создана: {message}')
                    )
                    if tables_to_create:
                        self.stdout.write('Созданные таблицы:')
                        for model in tables_to_create:
                            self.stdout.write(f'  - {model.get_table_name()}')
                    elif empty:
                        self.stdout.write('  - Пустая миграция')
            else:
                self.stdout.write(
                    self.style.WARNING('Миграция не создана (нет изменений)')
                )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при создании миграции: {e}')
            )
            sys.exit(1)
    
    def _get_existing_tables(self):
        """Получает список существующих таблиц в базе данных"""
        try:
            if hasattr(db, 'engine') and db.engine:
                # Для SQLAlchemy
                with db.engine.connect() as connection:
                    if db.engine.dialect.name == 'sqlite':
                        result = connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    elif db.engine.dialect.name == 'postgresql':
                        result = connection.execute("SELECT tablename FROM pg_tables WHERE schemaname='public'")
                    elif db.engine.dialect.name == 'mysql':
                        result = connection.execute("SHOW TABLES")
                    else:
                        # Для других баз данных используем общий подход
                        result = connection.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
                    
                    tables = [row[0] for row in result.fetchall()]
                    return tables
            return []
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'Предупреждение: не удалось получить список таблиц: {e}')
            )
            return []
    
    def _import_all_models(self):
        """Импортирует все модели для регистрации в ModelMeta"""
        try:
            # Импортируем модели из contrib
            import cotlette.contrib.auth.users.models
            import cotlette.contrib.auth.groups.models
            import cotlette.contrib.admin.models
            
            # Импортируем модели из приложений проекта
            try:
                import apps.home.models
            except ImportError:
                pass
                
        except ImportError as e:
            self.stdout.write(
                self.style.WARNING(f'Предупреждение: не удалось импортировать некоторые модели: {e}')
            )
    
    def _get_latest_migration_file(self):
        """Получает путь к последнему созданному файлу миграции"""
        try:
            versions_dir = Path('migrations/versions')
            if versions_dir.exists():
                migration_files = list(versions_dir.glob('*.py'))
                if migration_files:
                    # Возвращаем самый новый файл
                    return str(max(migration_files, key=lambda x: x.stat().st_mtime))
        except:
            pass
        return None
    
    def _is_migration_empty(self, migration_file):
        """Проверяет, является ли миграция пустой"""
        try:
            with open(migration_file, 'r') as f:
                content = f.read()
                # Миграция считается пустой, если в ней нет SQL команд
                # Ищем SQL команды в upgrade функции
                if 'op.execute(' in content:
                    return False
                # Если есть только pass или пустые функции, считаем пустой
                if 'pass' in content and 'def upgrade():' in content and 'def downgrade():' in content:
                    return True
                return False
        except:
            return False
    
    def _remove_empty_migration(self, migration_file):
        """Удаляет пустую миграцию"""
        try:
            os.remove(migration_file)
        except:
            pass 