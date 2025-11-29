"""
Admin registration for the movies app.

Register the ``Movie`` model with Django's admin site so that films can be
added, edited and deleted via the graphical interface.  The ``list_display``
tuple defines which fields should appear in the list view of the admin.
"""

from django.contrib import admin  # type: ignore

from .models import Movie


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    """Admin configuration for the Movie model."""

    list_display = (
        "title",
        "director",
        "rating",
        "release_year",
        "duration_minutes",
        "genre",
    )
    search_fields = ("title", "director")
    list_filter = ("genre", "rating", "release_year")