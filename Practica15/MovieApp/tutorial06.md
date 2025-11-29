# Tutorial 06 - Aplicacion Polls Completa

Esta guia resume los tutoriales oficiales de Django 5.0 (01, 02, 03, 04 y 06) para construir la aplicacion de encuestas `polls` dentro de un proyecto `mysite`. Cada seccion repasa los comandos y archivos indispensables para que puedas recrear la aplicacion desde cero en Practica15.

## Requisitos previos

- Python 3.10 o superior instalado en el sistema.
- Terminal con acceso a `py` (Windows) o `python3`.
- Conocimientos basicos de linea de comandos.
- Opcional: editor con soporte para Django.

## Preparar el entorno

```powershell
mkdir mysite
cd mysite
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install "django==5.0.*"
```

Es recomendable guardar las dependencias en un `requirements.txt` para compartir el proyecto con otras personas.

## 1. Tutorial 01: Proyecto base y primera vista

### 1.1 Crear el proyecto `mysite`

```powershell
django-admin startproject mysite .
```

Estructura inicial:

```
mysite/
    manage.py
    mysite/
        __init__.py
        settings.py
        urls.py
        asgi.py
        wsgi.py
```

`manage.py` es el comando de entrada para tareas administrativas, mientras que el paquete `mysite` contiene la configuracion principal.

### 1.2 Ejecutar el servidor de desarrollo

```powershell
python manage.py runserver
```

Visita `http://127.0.0.1:8000/` para confirmar que el proyecto responde.

### 1.3 Crear la aplicacion `polls`

```powershell
python manage.py startapp polls
```

Agrega la app dentro de `mysite/settings.py`:

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "polls.apps.PollsConfig",
]
```

### 1.4 Configurar las URL iniciales

`polls/views.py`:

```python
from django.http import HttpResponse

def index(request):
    return HttpResponse("Hola, estas en la portada de encuestas.")
```

`polls/urls.py`:

```python
from django.urls import path
from . import views

app_name = "polls"

urlpatterns = [
    path("", views.index, name="index"),
]
```

`mysite/urls.py`:

```python
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("polls/", include("polls.urls")),
    path("admin/", admin.site.urls),
]
```

Con esto ya puedes navegar a `http://127.0.0.1:8000/polls/`.

## 2. Tutorial 02: Modelos, migraciones y sitio de administracion

### 2.1 Definir los modelos

`polls/models.py`:

```python
import datetime
from django.db import models
from django.utils import timezone

class Question(models.Model):
    question_text = models.CharField("texto de la pregunta", max_length=200)
    pub_date = models.DateTimeField("fecha de publicacion")

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField("opcion", max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text
```

### 2.2 Crear las tablas

```powershell
python manage.py makemigrations polls
python manage.py migrate
```

### 2.3 Explorar la API de datos

```powershell
python manage.py shell
```

En el shell interactivo:

```python
from polls.models import Question, Choice
from django.utils import timezone

q = Question.objects.create(question_text="Cual es tu lenguaje favorito?", pub_date=timezone.now())
q.choice_set.create(choice_text="Python", votes=0)
q.choice_set.create(choice_text="JavaScript", votes=0)
```

### 2.4 Configurar el sitio de administracion

`polls/admin.py`:

```python
from django.contrib import admin
from .models import Question, Choice

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["question_text"]}),
        ("Informacion de fecha", {"fields": ["pub_date"], "classes": ["collapse"]}),
    ]
    inlines = [ChoiceInline]
    list_display = ["question_text", "pub_date", "was_published_recently"]
    list_filter = ["pub_date"]
    search_fields = ["question_text"]

admin.site.register(Choice)
```

Crea un usuario administrador:

```powershell
python manage.py createsuperuser
```

Inicia el servidor y visita `http://127.0.0.1:8000/admin/` para gestionar preguntas y opciones.

## 3. Tutorial 03: Vistas, plantillas y formulario de voto

### 3.1 Plantillas

Estructura dentro de la app:

```
polls/
    templates/
        polls/
            index.html
            detail.html
            results.html
```

`polls/templates/polls/index.html`:

```html
{% if latest_question_list %}
    <ul>
    {% for question in latest_question_list %}
        <li><a href="{% url 'polls:detail' question.id %}">{{ question.question_text }}</a></li>
    {% endfor %}
    </ul>
{% else %}
    <p>No hay encuestas disponibles.</p>
{% endif %}
```

`polls/templates/polls/detail.html`:

```html
<h1>{{ question.question_text }}</h1>

{% if error_message %}
    <p><strong>{{ error_message }}</strong></p>
{% endif %}

<form action="{% url 'polls:vote' question.id %}" method="post">
    {% csrf_token %}
    {% for choice in question.choice_set.all %}
        <label>
            <input type="radio" name="choice" value="{{ choice.id }}">
            {{ choice.choice_text }}
        </label><br>
    {% endfor %}
    <button type="submit">Votar</button>
</form>
```

`polls/templates/polls/results.html`:

```html
<h1>{{ question.question_text }}</h1>
<ul>
    {% for choice in question.choice_set.all %}
        <li>{{ choice.choice_text }} -- {{ choice.votes }} voto{{ choice.votes|pluralize }}</li>
    {% endfor %}
</ul>
<a href="{% url 'polls:detail' question.id %}">Votar otra vez</a>
```

### 3.2 Vistas basadas en funciones

`polls/views.py`:

```python
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from .models import Question, Choice

def index(request):
    latest_question_list = Question.objects.order_by("-pub_date")[:5]
    context = {"latest_question_list": latest_question_list}
    return render(request, "polls/index.html", context)

def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/detail.html", {"question": question})

def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/results.html", {"question": question})

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "Debes seleccionar una opcion.",
            },
        )
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))
```

`polls/urls.py` actualizado:

```python
from django.urls import path
from . import views

app_name = "polls"

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:question_id>/", views.detail, name="detail"),
    path("<int:question_id>/results/", views.results, name="results"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
]
```

## 4. Tutorial 04: Vistas genericas basadas en clases

Refactoriza `polls/views.py` para aprovechar las vistas genericas:

```python
from django.views import generic
from django.utils import timezone

class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:5]

class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now())

class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"
```

Actualiza `polls/urls.py`:

```python
from django.urls import path
from . import views

app_name = "polls"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
]
```

La vista `vote` permanece como funcion porque maneja logica de formularios y redirecciones.

## 5. Tutorial 06: Archivos estaticos

### 5.1 Estructura de archivos estaticos

Crea el directorio `polls/static/polls/` y la hoja de estilos `style.css`:

```css
li a {
    color: #1d4ed8;
}

body {
    background: #f1f5f9;
    font-family: system-ui, sans-serif;
    margin: 2rem;
}
```

### 5.2 Cargar la hoja de estilos en la plantilla

`polls/templates/polls/index.html` al inicio:

```html
{% load static %}
<link rel="stylesheet" href="{% static 'polls/style.css' %}">
```

Si ya existe contenido, asegurate de que `{% load static %}` sea la primera etiqueta en el archivo.

### 5.3 Configuracion adicional

En `mysite/settings.py` puedes declarar un directorio global de recursos estaticos:

```python
STATIC_URL = "static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
```

Para despliegue en produccion, define:

```python
STATIC_ROOT = BASE_DIR / "staticfiles"
```

Luego ejecuta:

```powershell
python manage.py collectstatic
```

## Verificacion manual y siguientes pasos

1. Inicia el servidor de desarrollo con `python manage.py runserver`.
2. Crea preguntas y opciones desde el panel de administracion.
3. Visita `/polls/` para confirmar la apariencia y el flujo de voto.
4. Opcional: agrega pruebas automatizadas (`python manage.py test`) y despliega usando un servicio como Railway, Render o un servidor propio.

Con estos pasos replicaste la aplicacion `polls` completa siguiendo los tutoriales oficiales 01, 02, 03, 04 y 06 de Django 5.0. Ajusta los estilos, textos y configuraciones segun las necesidades de tu practica.
