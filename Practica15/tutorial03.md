# Tutorial 3 – Plantillas y vistas más complejas

La tercera parte introduce el sistema de plantillas de Django y la creación de vistas que leen datos de los modelos.

## Directorios de plantillas

El archivo de configuración `TEMPLATES` indica a Django cómo cargar las plantillas.  Por defecto, la opción `APP_DIRS` está activada, lo que hace que Django busque una subcarpeta `templates` dentro de cada aplicación【200128532011530†L231-L240】.  Se recomienda crear un subdirectorio adicional con el nombre de la app para evitar conflictos entre plantillas homónimas【200128532011530†L244-L251】.  Por ejemplo, para la app `polls` la estructura sería `polls/templates/polls/index.html`.

## Mostrar datos en una plantilla

Las plantillas permiten insertar valores del contexto mediante la sintaxis `{{ variable }}` y utilizar bloques de control `{% %}`.  Para mostrar la lista de preguntas se define una plantilla que recorre la variable `latest_question_list` y crea enlaces hacia el detalle de cada pregunta【200128532011530†L255-L266】.

La vista se actualiza para consultar las preguntas en la base de datos, cargar la plantilla y pasarle un diccionario de contexto【200128532011530†L273-L310】.  Django ofrece la función de ayuda `render(request, template_name, context)` que combina estas operaciones y devuelve automáticamente un `HttpResponse`【200128532011530†L295-L318】.

## Vistas de detalle y gestión de errores

Para mostrar el detalle de una pregunta se crea una vista que recibe el parámetro `question_id`.  La vista intenta recuperar la pregunta con `Question.objects.get(pk=question_id)`; si no existe, se lanza una excepción `Http404`【200128532011530†L333-L339】.  Django también proporciona el atajo `get_object_or_404()` para encapsular esa lógica【200128532011530†L360-L369】.  La plantilla de detalle (`polls/detail.html`) puede acceder a `question` y mostrar el texto de la pregunta o sus opciones.