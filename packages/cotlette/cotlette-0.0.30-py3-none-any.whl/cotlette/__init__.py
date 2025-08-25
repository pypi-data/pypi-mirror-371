__version__ = "0.0.30"

import os
import logging
# import importlib.util
import importlib

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from cotlette.conf import settings
from cotlette import shortcuts



logger = logging.getLogger("uvicorn")


class Cotlette(FastAPI):

    def __init__(self):
        super().__init__()

        self.settings = settings
        self.shortcuts = shortcuts

        # Get absolute path to current directory
        self.cotlette_directory = os.path.dirname(os.path.abspath(__file__))
        
        # Include routers
        self.include_routers()
        self.include_templates()
        self.include_static()

    def include_routers(self):
        # Check and import installed applications
        logger.info(f"Loading apps and routers:")
        for app_path in self.settings.INSTALLED_APPS:
            # Dynamically import module
            module = importlib.import_module(app_path)
            logger.info(f"✅'{app_path}'")

            # If module contains routers, include them
            if hasattr(module, "router"):
                self.include_router(module.router)
                logger.info(f"✅'{app_path}.router'")
            else:
                logger.warning(f"⚠️ '{app_path}.router'")

    def include_templates(self):
        # Connect internal Cotlette templates (e.g., admin templates)
        internal_template_dirs = [
            os.path.join(self.cotlette_directory, "contrib", "templates")
        ]
        for template in self.settings.TEMPLATES:
            # Add internal templates to user template directories
            template_dirs = template.get("DIRS", [])
            # Convert relative paths to absolute
            template_dirs = [os.path.join(self.settings.BASE_DIR, path) for path in template_dirs]
            # Add internal templates if not already present
            for internal_dir in internal_template_dirs:
                if internal_dir not in template_dirs:
                    template_dirs.append(internal_dir)
            template["DIRS"] = template_dirs
    def include_static(self):
        # Include framework static files
        internal_static_dir = os.path.join(self.cotlette_directory, "contrib", "static")
        self.mount("/admin_static", StaticFiles(directory=internal_static_dir), name="admin_static")

        # Include static files from STATICFILES_DIRS
        if hasattr(self.settings, 'STATICFILES_DIRS') and self.settings.STATICFILES_DIRS:
            for static_dir in self.settings.STATICFILES_DIRS:
                if os.path.exists(static_dir):
                    self.mount("/static", StaticFiles(directory=static_dir), name="static")
                    break  # Mount only the first existing directory
        # Fallback to default static directory
        elif self.settings.STATIC_URL:
            static_dir = os.path.join(self.settings.BASE_DIR, self.settings.STATIC_URL)
            if os.path.exists(static_dir):
                self.mount("/static", StaticFiles(directory=static_dir), name="static")