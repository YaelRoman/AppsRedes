"""
Database models for the movies app.

The ``Movie`` model describes a film with various attributes such as title,
director, rating, year of release, running time and genre.  The genre field
uses a set of choices to enforce a limited selection of categories.
"""

from django.db import models  # type: ignore


class Movie(models.Model):
    """A model representing a single film."""

    class Genre(models.TextChoices):
        """Enumeration of possible movie genres."""

        COMEDY = "COM", "Comedia"
        ROMANCE = "ROM", "Romance"
        ADVENTURE = "ADV", "Aventura"
        HORROR = "HOR", "Terror"
        ACTION = "ACC", "Acción"
        DRAMA = "DRA", "Drama"
        SCI_FI = "SCI", "Ciencia ficción"
        OTHER = "OTH", "Otro"

    title = models.CharField(max_length=200, help_text="Título de la película")
    director = models.CharField(max_length=100, help_text="Director de la película")
    rating = models.CharField(max_length=10, help_text="Clasificación (por ejemplo, PG-13)")
    release_year = models.PositiveIntegerField(help_text="Año de estreno")
    duration_minutes = models.PositiveIntegerField(help_text="Duración en minutos")
    genre = models.CharField(
        max_length=3,
        choices=Genre.choices,
        default=Genre.OTHER,
        help_text="Género de la película",
    )

    class Meta:
        ordering = ["title"]
        verbose_name = "Película"
        verbose_name_plural = "Películas"

    def __str__(self) -> str:
        return f"{self.title} ({self.release_year})"