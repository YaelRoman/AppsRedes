"""
Configuration for the movies application.

This file defines the AppConfig subclass used by Django to configure the
application.  It also sets a human‑readable name for the app which will
appear in the admin interface.
"""

from django.apps import AppConfig  # type: ignore


class MoviesConfig(AppConfig):
    """Django configuration for the movies app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "movies"
    verbose_name = "Películas"