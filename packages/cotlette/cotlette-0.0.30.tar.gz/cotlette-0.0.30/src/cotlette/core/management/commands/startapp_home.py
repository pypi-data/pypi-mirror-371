from cotlette.core.management.templates import TemplateCommand


class Command(TemplateCommand):
    help = (
        "Creates a Cotlette home app directory structure with basic functionality "
        "including models, views, admin, API, and templates."
    )
    missing_args_message = "You must provide an application name."

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--with-templates",
            action="store_true",
            help="Include HTML templates (default: True)",
        )
        parser.add_argument(
            "--with-admin",
            action="store_true",
            help="Include admin configuration (default: True)",
        )
        parser.add_argument(
            "--with-api",
            action="store_true",
            help="Include API endpoints (default: True)",
        )

    def handle(self, **options):
        app_name = options.pop("name")
        target = options.pop("directory")
        
        # Set default options for home app
        options["with_templates"] = options.pop("with_templates", True)
        options["with_admin"] = options.pop("with_admin", True)
        options["with_api"] = options.pop("with_api", True)
        options["is_home_app"] = True

        super().handle("app", app_name, target, **options)

