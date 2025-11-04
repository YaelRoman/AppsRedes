# Tutorial 4 – Procesar formularios y genéricos

En la cuarta parte del tutorial se añaden formularios para que los usuarios puedan votar y se muestra cómo simplificar vistas usando genéricos.

## Crear un formulario de voto

Se modifica la plantilla de detalle para incluir un elemento `<form>` que envía la elección del usuario mediante el método `POST`.  El valor de cada radio botón corresponde con el ID de la opción y el nombre del campo es `choice`【894166430582959†L89-L110】.  Es importante incluir el token CSRF `{% csrf_token %}` para proteger la aplicación contra ataques de falsificación de peticiones【894166430582959†L113-L127】.

La vista `vote()` recupera la pregunta y luego intenta obtener la opción seleccionada a partir de `request.POST['choice']`.  Si no se seleccionó nada, vuelve a renderizar la plantilla con un mensaje de error; de lo contrario aumenta el contador de votos y redirige a la página de resultados【894166430582959†L149-L171】.  Se utiliza `HttpResponseRedirect` junto con `reverse()` para construir la URL de la vista de resultados.

## Vistas genéricas

Más adelante el tutorial muestra cómo reducir código utilizando *generic class-based views*.  Estas clases proporcionan implementaciones comunes de vistas de lista y de detalle, y permiten especificar simplemente el modelo y la plantilla.  Aunque esa sección está en el *Tutorial 5*, entender cómo funciona el formulario en el Tutorial 4 es crucial para desarrollar aplicaciones interactivas.