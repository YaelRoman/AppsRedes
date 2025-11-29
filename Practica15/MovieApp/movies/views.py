"""
Views for the movies app.

Currently only a simple list view is implemented.  It queries the database
for all stored ``Movie`` instances and passes them to a template for display.
"""

from django.shortcuts import render  # type: ignore

from .models import Movie


def index(request):
    """Render a page displaying all stored movies."""
    movies = Movie.objects.all().order_by("title")
    context = {"movies": movies}
    return render(request, "movies/index.html", context)