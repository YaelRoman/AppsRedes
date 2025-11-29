# Tutorial 2 – Trabajar con modelos y la base de datos

La segunda parte del tutorial se centra en configurar la base de datos y definir modelos.

## Configurar la base de datos

En `mysite/settings.py` se encuentra un diccionario `DATABASES`.  Django configura por defecto SQLite, una base de datos ligera incluida en Python, por lo que no hay que instalar nada adicional【138517189601939†L85-L93】.  También conviene ajustar la zona horaria (`TIME_ZONE`) a la propia región【138517189601939†L95-L100】.  Antes de usar cualquier aplicación incluida en `INSTALLED_APPS`, ejecuta la migración inicial:

```bash
python manage.py migrate
```

El comando `migrate` lee la lista de aplicaciones instaladas y crea las tablas necesarias en la base de datos【138517189601939†L122-L135】.

## Crear modelos

Un *modelo* representa la estructura de los datos.  En la app `polls` se definen dos modelos (`Question` y `Choice`) que se convierten en tablas de base de datos.  Cada modelo se define como una subclase de `models.Model` y declara sus campos como atributos de clase【138517189601939†L166-L183】.  Por ejemplo:

```python
from django.db import models

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
```

Una vez definidos los modelos, hay que informar al proyecto de que la aplicación está instalada añadiendo `'polls.apps.PollsConfig'` a `INSTALLED_APPS`.  Luego se generan las migraciones para la app y se aplican:

```bash
python manage.py makemigrations polls
python manage.py migrate
```

## Usar la API de objetos

Django crea una API de acceso a la base de datos a partir de los modelos: se puede crear, consultar, filtrar y ordenar objetos con métodos de Python.  Por ejemplo, `Question.objects.order_by("-pub_date")[:5]` obtiene las últimas cinco preguntas【200128532011530†L283-L290】.  La API es lazily evaluated, así que las consultas se ejecutan cuando se necesitan.  Además, la función `get_object_or_404()` permite recuperar un objeto o lanzar una excepción HTTP 404 si no existe【200128532011530†L360-L369】.