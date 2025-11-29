# Simulador Visual de Ataques de Contraseñas

Este proyecto es un simulador educativo que permite introducir una
contraseña, evaluar su fortaleza y observar cómo funcionan varias
técnicas de cracking de contraseñas en tiempo real.  La interfaz,
inspirada en un panel de operaciones de seguridad, ofrece un tema
oscuro, fuentes monoespaciadas y gráficos que muestran el progreso de
cada ataque.

## Características principales

1. **Análisis de contraseña**
   - Calcula la longitud, los conjuntos de caracteres utilizados (minúsculas, mayúsculas, dígitos, símbolos) y la entropía aproximada en bits empleando la fórmula \(\log_2(N^L)\)【671562893711359†L63-L69】.
   - Clasifica la contraseña en categorías que van de *Muy débil* a *Muy fuerte* usando umbrales orientativos basados en ejemplos de entropía de 38 bits para contraseñas de 8 minúsculas y 79 bits para contraseñas de 12 caracteres mezclados【325584728368036†L420-L427】.
   - Proporciona sugerencias para mejorar la fortaleza de la contraseña.

2. **Ataques implementados**
   Cada ataque se ejecuta en un hilo separado y se puede detener en cualquier momento.  Las búsquedas se limitan para mantener una demo fluida.

   - **Fuerza bruta**: genera todas las combinaciones posibles de un alfabeto reducido hasta una longitud máxima.
   - **Diccionario**: recorre una lista de palabras comunes (incluida en `dictionary.txt`).
   - **Híbrido**: combina palabras del diccionario con sufijos numéricos (por defecto de 0 a 200).
   - **Máscara**: acepta un patrón sencillo (por defecto `?u?l?l?l?d?d`) que especifica tipos de caracteres por posición.
   - **Reglas**: aplica transformaciones típicas (capitalización, sustitución de letras por números, sufijos comunes) a palabras del diccionario.
   - **Tabla arcoíris**: realiza una búsqueda en una pequeña tabla precomputada (`rainbow_table.txt`) para ilustrar la rapidez de esta técnica.

3. **Interfaz de usuario**
   - Tema oscuro tipo *hacker dashboard* con pestañas para cada ataque.
   - Barra de progreso, estadísticas de intentos, tiempo y velocidad de prueba.
   - Área de log estilo terminal que muestra los candidatos probados y mensajes del hilo.
   - Gráfico en tiempo real (basado en **pyqtgraph**) que representa la evolución de la velocidad de intentos.

## Instalación

1. Asegúrate de tener **Python 3.7** o superior.
2. Instala las dependencias necesarias (por ejemplo mediante `pip`):

   ```bash
   pip install pyqt5 pyqtgraph
   ```

3. Clona este repositorio o copia la carpeta `visual_password_attack_simulator` en tu entorno de trabajo.

## Uso

Para ejecutar la aplicación, ejecuta el módulo `dashboard`:

```bash
python -m visual_password_attack_simulator.ui.dashboard
```

Se abrirá una ventana donde podrás introducir una contraseña.  Tras pulsar
**Analizar**, se mostrará su fortaleza y se habilitarán las pestañas de
ataques.  Cada ataque se puede iniciar de forma independiente y
cancelar con el botón correspondiente.

## Aviso de responsabilidad

Este software está pensado exclusivamente con fines educativos.  No lo
utilices para vulnerar contraseñas ajenas ni para examinar contraseñas
reales en sistemas de producción.  Muchos detalles de los ataques se
han simplificado para que la demostración sea rápida y comprensible,
por lo que no refleja la complejidad de los ataques de cracking
reales.  Para proteger tus cuentas, usa contraseñas únicas, largas y
complejas, idealmente gestionadas mediante un gestor de contraseñas y
complementadas con métodos de autenticación multifactor.