from cotlette.core.management.templates import TemplateCommand
import os
import shutil
from ..utils import get_random_secret_key


SECRET_KEY_INSECURE_PREFIX = "insecure-"


class Command(TemplateCommand):
    help = (
        "Creates a Cotlette project directory structure for the given project "
        "name in the current directory or optionally in the given directory. "
        "Includes a home app with basic functionality."
    )
    missing_args_message = "You must provide a project name."

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--with-home",
            action="store_true",
            help="Create project with home app (default: True)",
        )
        parser.add_argument(
            "--no-home",
            action="store_true",
            help="Create project without home app",
        )

    def handle(self, **options):
        project_name = options.pop("name")
        target = options.pop("directory")
        with_home = options.pop("with_home", False)  # store_true по умолчанию False
        no_home = options.pop("no_home", False)      # store_true по умолчанию False

        # Create a random SECRET_KEY to put it in the main settings.
        options["secret_key"] = SECRET_KEY_INSECURE_PREFIX + get_random_secret_key()
        
        # Set home app option - по умолчанию создаем приложение home
        # Если явно указан --no-home, то не создаем
        # Если явно указан --with-home, то создаем
        # Если ничего не указано, то создаем по умолчанию
        create_home_app = not no_home  # По умолчанию True, если не указан --no-home
        options["create_home_app"] = create_home_app

        # First create the project
        super().handle("project", project_name, target, **options)
        
        # If we don't want home app, remove it
        if not create_home_app:
            project_dir = target if target else project_name
            home_app_dir = os.path.join(project_dir, "apps", "home")
            if os.path.exists(home_app_dir):
                shutil.rmtree(home_app_dir)
                print(f"Removed home app from {project_dir}")
            
            # Also remove home templates
            home_templates_dir = os.path.join(project_dir, "templates", "home")
            if os.path.exists(home_templates_dir):
                shutil.rmtree(home_templates_dir)
                print(f"Removed home templates from {project_dir}")
            
            # Update settings.py to remove home app
            settings_file = os.path.join(project_dir, "config", "settings.py")
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Remove home app from INSTALLED_APPS
                content = content.replace("    'apps.home',", "")
                content = content.replace("    \"apps.home\",", "")
                
                with open(settings_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"Updated {settings_file} to remove home app")
