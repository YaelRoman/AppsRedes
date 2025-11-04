# Tutorial 6 – Archivos estáticos

La última parte que se solicita abarca la gestión de *static files*.  Las aplicaciones web suelen necesitar archivos como CSS, imágenes o JavaScript para mejorar la presentación.

## Organización de archivos estáticos

Django incluye la aplicación `django.contrib.staticfiles` para recopilar y servir archivos estáticos.  Para cada app, se recomienda crear un directorio `static` dentro de la carpeta de la app y, dentro de él, otro subdirectorio con el nombre de la app para evitar colisiones entre ficheros de distintas aplicaciones【26685022252635†L96-L123】.  Así, para la app `polls` la hoja de estilos se ubica en `polls/static/polls/style.css`.  Esta estructura permite referirse al archivo en las plantillas como `polls/style.css`【26685022252635†L98-L113】.

Para aplicar la hoja de estilos, añade en la plantilla la etiqueta `{% load static %}` y un elemento `<link>` que utilice la etiqueta `{% static %}` para generar la URL correcta【26685022252635†L136-L143】.  Por ejemplo:

```html
{% load static %}
<link rel="stylesheet" href="{% static 'polls/style.css' %}">
```

Tras crear el archivo CSS y actualizar la plantilla, inicia o reinicia el servidor con `python manage.py runserver` y recarga la página: los enlaces deberían mostrarse con el nuevo estilo【26685022252635†L146-L154】.