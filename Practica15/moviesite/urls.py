"""
URL configuration for moviesite project.

The ``urlpatterns`` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/

Examples:
Function views
    1. Add an import:  ``from movies import views``
    2. Add a URL to urlpatterns:  ``path('', views.home, name='home')``

Including another URLconf
    1. Import the include() function: ``from django.urls import include, path``
    2. Add a URL to urlpatterns:  ``path('movies/', include('movies.urls'))``
"""

from django.contrib import admin  # type: ignore
from django.urls import include, path  # type: ignore

urlpatterns = [
    # Route the admin interface
    path("admin/", admin.site.urls),
    # Delegate movie‑related URLs to the movies app
    path("", include("movies.urls")),
]