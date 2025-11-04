"""
URL configuration for the movies app.

This module maps URL patterns to view callables.  Currently it exposes a
single route for the movie list view.  The routes are namespaced with the
app_name so that they can be referenced unambiguously from templates.
"""

from django.urls import path  # type: ignore

from . import views


app_name = "movies"

urlpatterns = [
    path("", views.index, name="index"),
]