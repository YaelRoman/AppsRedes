#!/usr/bin/env python3
from __future__ import annotations
import os, sqlite3, math
from flask import Flask, request, jsonify, Response, render_template_string, abort

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "alumnos_flask.db")

# ---------- DB helpers ----------
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS alumnos(
                matricula TEXT PRIMARY KEY,
                nombre    TEXT NOT NULL,
                edad      INTEGER NOT NULL
            )
        """)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def parse_float(val, name):
    try:
        return float(val)
    except (TypeError, ValueError):
        abort(json_error(400, f"Parameter '{name}' must be numeric"))

def json_error(status: int, message: str):
    resp = jsonify({"error": message})
    resp.status_code = status
    return resp


# ---------- PAGES (subpages with forms) ----------
INDEX_HTML = """
<!doctype html>
<html lang="es"><meta charset="utf-8">
<title>Inicio</title>
<h1>Hola Mundo</h1>
<p>Secciones:</p>
<ul>
  <li><a href="/math">Operaciones Matemáticas</a></li>
  <li><a href="/area">Cálculo de Áreas</a></li>
  <li><a href="/conversion">Conversión de Grados</a></li>
  <li><a href="/alumnos_ui">Gestión de Alumnos</a></li>
</ul>
"""

MATH_HTML = """
<!doctype html>
<html lang="es"><meta charset="utf-8">
<title>Operaciones Matemáticas</title>
<h1>Operaciones Matemáticas</h1>

<h2>Suma (POST con Query String)</h2>
<form id="sumarForm" method="post" action="/sumar">
  <label>a: <input type="number" name="a" step="any" required></label>
  <label>b: <input type="number" name="b" step="any" required></label>
  <button type="submit">Sumar</button>
</form>
<pre id="sumarOut"></pre>

<h2>Multiplicación (POST con JSON)</h2>
<form id="multForm">
  <label>a: <input type="number" name="a" step="any" required></label>
  <label>b: <input type="number" name="b" step="any" required></label>
  <button type="submit">Multiplicar</button>
</form>
<pre id="multOut"></pre>

<p><a href="/">Volver</a></p>

<script>
// Fuerza que el POST a /sumar use query string como lo pidió el enunciado
document.getElementById('sumarForm').addEventListener('submit', (e) => {
  e.preventDefault();
  const a = e.target.a.value;
  const b = e.target.b.value;
  fetch(`/sumar?a=${encodeURIComponent(a)}&b=${encodeURIComponent(b)}`, { method: 'POST' })
    .then(r => r.json()).then(j => sumarOut.textContent = JSON.stringify(j, null, 2))
    .catch(err => sumarOut.textContent = err);
});

// Para /multiplicar, el cuerpo debe ser JSON
document.getElementById('multForm').addEventListener('submit', (e) => {
  e.preventDefault();
  const a = e.target.a.value;
  const b = e.target.b.value;
  fetch('/multiplicar', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({a: Number(a), b: Number(b)})
  }).then(r => r.json()).then(j => multOut.textContent = JSON.stringify(j, null, 2))
    .catch(err => multOut.textContent = err);
});
</script>
"""

AREA_HTML = """
<!doctype html>
<html lang="es"><meta charset="utf-8">
<title>Cálculo de Áreas</title>
<h1>Cálculo de Áreas</h1>

<h2>Área de un Triángulo</h2>
<form id="triForm">
  <label>Base: <input type="number" name="base" step="any" required></label>
  <label>Altura: <input type="number" name="altura" step="any" required></label>
  <button type="submit">Calcular</button>
</form>
<pre id="triOut"></pre>

<h2>Área de un Círculo</h2>
<form id="cirForm">
  <label>Radio: <input type="number" name="radio" step="any" required></label>
  <button type="submit">Calcular</button>
</form>
<pre id="cirOut"></pre>

<p><a href="/">Volver</a></p>

<script>
document.getElementById('triForm').addEventListener('submit', (e)=>{
  e.preventDefault();
  const base = e.target.base.value, altura = e.target.altura.value;
  fetch('/area/triangulo', {method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({base: Number(base), altura: Number(altura)})})
  .then(r=>r.json()).then(j=>triOut.textContent = JSON.stringify(j,null,2));
});
document.getElementById('cirForm').addEventListener('submit', (e)=>{
  e.preventDefault();
  const radio = e.target.radio.value;
  fetch('/area/circulo', {method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({radio: Number(radio)})})
  .then(r=>r.json()).then(j=>cirOut.textContent = JSON.stringify(j,null,2));
});
</script>
"""

CONV_HTML = """
<!doctype html>
<html lang="es"><meta charset="utf-8">
<title>Conversión</title>
<h1>Conversión de Grados</h1>

<h2>Fahrenheit → Centígrados</h2>
<form id="f2cForm">
  <label>Fahrenheit: <input type="number" name="f" step="any" required></label>
  <button type="submit">Convertir</button>
</form>
<pre id="f2cOut"></pre>

<h2>Centígrados → Fahrenheit</h2>
<form id="c2fForm">
  <label>Centígrados: <input type="number" name="c" step="any" required></label>
  <button type="submit">Convertir</button>
</form>
<pre id="c2fOut"></pre>

<p><a href="/">Volver</a></p>

<script>
document.getElementById('f2cForm').addEventListener('submit', (e)=>{
  e.preventDefault();
  const f = e.target.f.value;
  fetch('/convertir/f2c', {method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({farenheit: Number(f)})})
  .then(r=>r.json()).then(j=>f2cOut.textContent = JSON.stringify(j,null,2));
});
document.getElementById('c2fForm').addEventListener('submit', (e)=>{
  e.preventDefault();
  const c = e.target.c.value;
  fetch('/convertir/c2f', {method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({centigrados: Number(c)})})
  .then(r=>r.json()).then(j=>c2fOut.textContent = JSON.stringify(j,null,2));
});
</script>
"""

ALUMNOS_HTML = """
<!doctype html>
<html lang="es"><meta charset="utf-8">
<title>Gestión de Alumnos</title>
<h1>Gestión de Alumnos</h1>

<h2>Crear Alumno (POST)</h2>
<form id="createForm">
  <label>Matrícula: <input name="matricula" required></label>
  <label>Nombre: <input name="nombre" required></label>
  <label>Edad: <input type="number" name="edad" required></label>
  <button type="submit">Guardar</button>
</form>
<pre id="createOut"></pre>

<h2>Actualizar Alumno (PUT)</h2>
<form id="updateForm">
  <label>Matrícula: <input name="matricula" required></label>
  <label>Nombre (opcional): <input name="nombre"></label>
  <label>Edad (opcional): <input type="number" name="edad"></label>
  <button type="submit">Actualizar</button>
</form>
<pre id="updateOut"></pre>

<h2>Borrar Alumno (DELETE)</h2>
<form id="deleteForm">
  <label>Matrícula: <input name="matricula" required></label>
  <button type="submit">Borrar</button>
</form>
<pre id="deleteOut"></pre>

<h2>Mostrar Alumno (GET)</h2>
<form id="getOneForm">
  <label>Matrícula: <input name="matricula" required></label>
  <button type="submit">Consultar</button>
</form>
<pre id="getOneOut"></pre>

<h2>Listar Todos (GET)</h2>
<button id="listBtn">Listar</button>
<pre id="listOut"></pre>

<p><a href="/">Volver</a></p>

<script>
// Helpers fetch JSON
async function postJSON(url, obj, method='POST'){
  const r = await fetch(url, {method, headers:{'Content-Type':'application/json'}, body: JSON.stringify(obj)});
  return await r.json();
}
async function simpleJSON(url, method='GET'){
  const r = await fetch(url, {method});
  return await r.json();
}

createForm.addEventListener('submit', async (e)=>{
  e.preventDefault();
  const j = await postJSON('/alumnos', {
    matricula: e.target.matricula.value,
    nombre: e.target.nombre.value,
    edad: Number(e.target.edad.value)
  }, 'POST');
  createOut.textContent = JSON.stringify(j, null, 2);
});

updateForm.addEventListener('submit', async (e)=>{
  e.preventDefault();
  const id = e.target.matricula.value;
  const payload = {};
  if (e.target.nombre.value) payload.nombre = e.target.nombre.value;
  if (e.target.edad.value) payload.edad = Number(e.target.edad.value);
  const j = await postJSON('/alumnos/' + encodeURIComponent(id), payload, 'PUT');
  updateOut.textContent = JSON.stringify(j, null, 2);
});

deleteForm.addEventListener('submit', async (e)=>{
  e.preventDefault();
  const id = e.target.matricula.value;
  const j = await simpleJSON('/alumnos/' + encodeURIComponent(id), 'DELETE');
  deleteOut.textContent = JSON.stringify(j, null, 2);
});

getOneForm.addEventListener('submit', async (e)=>{
  e.preventDefault();
  const id = e.target.matricula.value;
  const j = await simpleJSON('/alumnos/' + encodeURIComponent(id), 'GET');
  getOneOut.textContent = JSON.stringify(j, null, 2);
});

listBtn.addEventListener('click', async ()=>{
  const j = await simpleJSON('/alumnos', 'GET');
  listOut.textContent = JSON.stringify(j, null, 2);
});
</script>
"""

@app.route("/")
def index():
    return render_template_string(INDEX_HTML)

@app.route("/math")
def math_page():
    return render_template_string(MATH_HTML)

@app.route("/area")
def area_page():
    return render_template_string(AREA_HTML)

@app.route("/conversion")
def conversion_page():
    return render_template_string(CONV_HTML)

@app.route("/alumnos_ui")
def alumnos_ui():
    return render_template_string(ALUMNOS_HTML)


# ---------- API endpoints ----------
# 1) Static HTML “Hola Mundo” already satisfied by GET "/"

# 2) Web service Sumar: POST + query string (also accepts form or JSON fallback)
@app.post("/sumar")
def sumar():
    a = request.args.get("a")  # query string (as required)
    b = request.args.get("b")
    if a is None or b is None:
        # accept form or JSON if present (useful when not hitting from JS)
        if request.is_json:
            data = request.get_json(silent=True) or {}
            a, b = data.get("a"), data.get("b")
        else:
            a, b = request.form.get("a"), request.form.get("b")
    a = parse_float(a, "a")
    b = parse_float(b, "b")
    return jsonify({"resultado": a + b})

# 3) Web service Multiplicar: POST JSON {a,b}
@app.post("/multiplicar")
def multiplicar():
    data = request.get_json(silent=True) or {}
    if "a" not in data or "b" not in data:
        return json_error(400, "JSON body with fields 'a' and 'b' is required")
    a = parse_float(data["a"], "a")
    b = parse_float(data["b"], "b")
    return jsonify({"resultado": a * b})

# 4) Área de Triángulo y Círculo (aceptan JSON o form)
@app.post("/area/triangulo")
def area_triangulo():
    base = (request.get_json(silent=True) or {}).get("base") if request.is_json else request.form.get("base")
    altura = (request.get_json(silent=True) or {}).get("altura") if request.is_json else request.form.get("altura")
    base = parse_float(base, "base")
    altura = parse_float(altura, "altura")
    return jsonify({"area": 0.5 * base * altura})

@app.post("/area/circulo")
def area_circulo():
    radio = (request.get_json(silent=True) or {}).get("radio") if request.is_json else request.form.get("radio")
    radio = parse_float(radio, "radio")
    return jsonify({"area": math.pi * radio * radio})

# 5) Conversión F↔C (JSON o form)
@app.post("/convertir/f2c")
def f2c():
    v = (request.get_json(silent=True) or {}).get("farenheit") if request.is_json else request.form.get("farenheit")
    f = parse_float(v, "farenheit")
    return jsonify({"centigrados": (f - 32) * 5.0 / 9.0})

@app.post("/convertir/c2f")
def c2f():
    v = (request.get_json(silent=True) or {}).get("centigrados") if request.is_json else request.form.get("centigrados")
    c = parse_float(v, "centigrados")
    return jsonify({"farenheit": c * 9.0 / 5.0 + 32})

# 6) CRUD de Alumnos (REST + UI compatible)
@app.post("/alumnos")
def alumnos_create():
    data = request.get_json(silent=True) or request.form
    m = data.get("matricula"); n = data.get("nombre"); e = data.get("edad")
    if not (m and n and e is not None):
        return json_error(400, "matricula, nombre, edad are required")
    try:
        e = int(e)
    except (TypeError, ValueError):
        return json_error(400, "edad must be integer")
    with get_db() as conn:
        try:
            conn.execute("INSERT INTO alumnos(matricula,nombre,edad) VALUES(?,?,?)", (m, n, e))
        except sqlite3.IntegrityError:
            return json_error(400, f"Alumno with matrícula {m} already exists")
    return jsonify({"mensaje": "Alumno creado correctamente"}), 201

@app.get("/alumnos")
def alumnos_list():
    with get_db() as conn:
        rows = [dict(r) for r in conn.execute("SELECT matricula,nombre,edad FROM alumnos ORDER BY matricula")]
    return jsonify({"alumnos": rows})

@app.get("/alumnos/<matricula>")
def alumnos_get(matricula):
    with get_db() as conn:
        row = conn.execute("SELECT matricula,nombre,edad FROM alumnos WHERE matricula=?", (matricula,)).fetchone()
        if not row:
            return json_error(404, f"Alumno {matricula} not found")
    return jsonify(dict(row))

@app.put("/alumnos/<matricula>")
def alumnos_update(matricula):
    data = request.get_json(silent=True) or {}
    nombre = data.get("nombre")
    edad   = data.get("edad")
    if nombre is None and edad is None:
        return json_error(400, "Provide at least one field (nombre or edad)")
    if edad is not None:
        try: edad = int(edad)
        except (TypeError, ValueError): return json_error(400, "edad must be integer")
    with get_db() as conn:
        cur = conn.execute("SELECT 1 FROM alumnos WHERE matricula=?", (matricula,)).fetchone()
        if not cur: return json_error(404, f"Alumno {matricula} not found")
        sets, params = [], []
        if nombre is not None: sets.append("nombre=?"); params.append(nombre)
        if edad   is not None: sets.append("edad=?");   params.append(edad)
        params.append(matricula)
        conn.execute(f"UPDATE alumnos SET {', '.join(sets)} WHERE matricula=?", params)
    return jsonify({"mensaje": "Alumno actualizado correctamente"})

@app.delete("/alumnos/<matricula>")
def alumnos_delete(matricula):
    with get_db() as conn:
        cur = conn.execute("SELECT 1 FROM alumnos WHERE matricula=?", (matricula,)).fetchone()
        if not cur: return json_error(404, f"Alumno {matricula} not found")
        conn.execute("DELETE FROM alumnos WHERE matricula=?", (matricula,))
    return jsonify({"mensaje": "Alumno eliminado correctamente"})


if __name__ == "__main__":
    init_db()
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    app.run(host=host, port=port, debug=False)
