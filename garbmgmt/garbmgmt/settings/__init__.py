"""Settings package. Select the active settings module via
the DJANGO_SETTINGS_MODULE environment variable.

Examples:
  DJANGO_SETTINGS_MODULE=garbmgmt.settings.development
  DJANGO_SETTINGS_MODULE=garbmgmt.settings.production
"""

__all__ = ["base", "development", "production"]
