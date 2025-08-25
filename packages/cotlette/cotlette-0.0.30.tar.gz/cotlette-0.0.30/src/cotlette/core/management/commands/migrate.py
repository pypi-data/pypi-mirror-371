from cotlette.core.management.base import BaseCommand
from cotlette.core.database.migrations import migration_manager
import sys


class Command(BaseCommand):
    help = "Применяет миграции к базе данных"

    def add_arguments(self, parser):
        parser.add_argument(
            '--revision', '-r',
            type=str,
            default='head',
            help='Ревизия для применения (по умолчанию "head")'
        )
        parser.add_argument(
            '--fake',
            action='store_true',
            help='Отметить миграцию как примененную без выполнения'
        )
        parser.add_argument(
            '--show-plan',
            action='store_true',
            help='Показать план миграций без применения'
        )

    def handle(self, *args, **options):
        revision = options.get('revision', 'head')
        fake = options.get('fake', False)
        show_plan = options.get('show_plan', False)
        
        try:
            # Инициализируем систему миграций если нужно
            migration_manager.init()
            
            # Получаем текущую ревизию
            current = migration_manager.current()
            self.stdout.write(
                self.style.SUCCESS(f'Текущая ревизия: {current or "нет"}')
            )
            
            if show_plan:
                # Показываем план миграций
                self.stdout.write(
                    self.style.SUCCESS(f'План миграций до ревизии: {revision}')
                )
                # Здесь можно добавить логику для показа плана
                return
            
            if fake:
                # Отмечаем миграцию как примененную
                migration_manager.stamp(revision)
                self.stdout.write(
                    self.style.SUCCESS(f'Миграция отмечена как примененная: {revision}')
                )
            else:
                # Применяем миграции
                migration_manager.upgrade(revision)
                self.stdout.write(
                    self.style.SUCCESS(f'Миграции применены до ревизии: {revision}')
                )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при применении миграций: {e}')
            )
            sys.exit(1) 