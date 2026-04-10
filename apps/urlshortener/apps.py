from django.apps import AppConfig


class UrlShortenerConfig(AppConfig):
    """Django app configuration for the urlshortener app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.urlshortener'
