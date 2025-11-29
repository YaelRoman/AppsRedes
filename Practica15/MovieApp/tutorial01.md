# Tutorial 1 – Crear un proyecto y la primera vista

El tutorial oficial de Django comienza explicando cómo crear un nuevo proyecto y una aplicación.  Para ello se debe seguir estos pasos:

## Crear el proyecto

Desde la terminal, crea una carpeta para el código (`djangotutorial`) y luego ejecuta el comando `startproject`.  Este comando genera un directorio del proyecto con varios archivos, incluido `manage.py` y un paquete de Python con la configuración de Django.  El propio tutorial destaca que conviene evitar nombres que choquen con componentes internos de Python o de Django 【472747320606723†L118-L146】.  Por ejemplo:

```bash
mkdir djangotutorial
django‑admin startproject mysite djangotutorial
```

Esto creará los archivos `manage.py` y el paquete `mysite` con `settings.py`, `urls.py`, `wsgi.py` y `asgi.py`【472747320606723†L146-L174】.

## Crear una aplicación

En Django la lógica se agrupa en *aplicaciones*.  Una aplicación se crea con el comando `startapp`.  Colócate en el mismo directorio que contiene `manage.py` y ejecuta:

```bash
python manage.py startapp polls
```

El resultado es un nuevo directorio con archivos como `admin.py`, `apps.py`, `models.py`, `tests.py`, `views.py` y una carpeta `migrations`【472747320606723†L260-L283】.  Las aplicaciones son desacopladas: pueden formar parte de varios proyectos y distribuirse por separado【472747320606723†L254-L258】.

## Escribir la primera vista

Para devolver una respuesta al navegador se define una *vista*.  En `polls/views.py` se añade una función que devuelve un objeto `HttpResponse` con un texto de bienvenida【472747320606723†L286-L297】.  Para que la vista sea accesible se necesita un archivo de configuración de URLs dentro de la aplicación.  Crea `polls/urls.py` con un `urlpatterns` que mapee la ruta raíz a la vista y añade un `include()` en el archivo principal `mysite/urls.py` para delegar todas las rutas que empiecen con `polls/`【472747320606723†L329-L346】.  Finalmente se arranca el servidor con:

```bash
python manage.py runserver
```

y visitando `http://localhost:8000/polls/` se verá el texto *“Hello, world. You’re at the polls index.”*【472747320606723†L361-L372】.