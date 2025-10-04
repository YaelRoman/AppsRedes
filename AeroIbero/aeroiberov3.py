import graphs
import compRoutes
import os, sqlite3, random, string, re, unicodedata
from tkinter import *
from tkinter import ttk, messagebox
from tkinter import filedialog
from tkinter import simpledialog


email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
phone_pattern = re.compile(r'^\+?\d{1,4}[-.\s]?\(?\d{1,3}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}$')


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "Databases", "AeroIbero.db")
LAST_ROUTES = {"costo": None, "distancia": None, "tiempo": None}

RAZA_COMBOS: list[ttk.Combobox] = [] 
RAZA_OPTIONS: list[str] = []
RAZA_SENTINEL = "Otra…"

DARK_BG   = "#222"
DARK_FG   = "#eee"
FIELD_BG  = "#333"
BTN_BG    = "#444"
ACCENT_BG = "#874CAF"

# Tema oscuro para los elementos
def _style_ttk():
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass

    style.configure(".", background=DARK_BG, foreground=DARK_FG)

    style.configure("TFrame", background=DARK_BG)
    style.configure("TLabelframe", background=DARK_BG, foreground=DARK_FG)
    style.configure("TLabel", background=DARK_BG, foreground=DARK_FG)

    style.configure("TButton", background=BTN_BG, foreground=DARK_FG)
    style.map("TButton",
              background=[("active", FIELD_BG)],
              foreground=[("disabled", "#888")])

    style.configure("TEntry", fieldbackground=FIELD_BG, foreground=DARK_FG, insertcolor=DARK_FG)
    style.configure("TCombobox",
                    fieldbackground=FIELD_BG,
                    background=FIELD_BG,
                    foreground=DARK_FG)
    style.map("TCombobox",
              fieldbackground=[("readonly", FIELD_BG)],
              foreground=[("readonly", DARK_FG)])

    style.configure("Vertical.TScrollbar", background=BTN_BG, troughcolor=DARK_BG, arrowcolor=DARK_FG)
    style.configure("Horizontal.TScrollbar", background=BTN_BG, troughcolor=DARK_BG, arrowcolor=DARK_FG)

    style.configure("Treeview",
                    background=FIELD_BG,
                    fieldbackground=FIELD_BG,
                    foreground=DARK_FG)
    style.map("Treeview", background=[("selected", "#555")])

def _theme_tk_widget(w):
    try:
        if w.winfo_class() == "Canvas":
            w.configure(bg=DARK_BG, highlightthickness=0, bd=0)
        from tkinter import Frame, LabelFrame, Label, Entry, Button, Radiobutton, Toplevel
        if isinstance(w, (Frame, LabelFrame, Toplevel)):
            w.configure(bg=DARK_BG)
        elif isinstance(w, Label):
            w.configure(bg=DARK_BG, fg=DARK_FG)
        elif isinstance(w, Entry):
            w.configure(bg=FIELD_BG, fg=DARK_FG, insertbackground=DARK_FG)
        elif isinstance(w, Button):
            w.configure(bg=BTN_BG, fg=DARK_FG, activebackground=FIELD_BG, activeforeground=DARK_FG)
        elif isinstance(w, Radiobutton):
            w.configure(bg=DARK_BG, fg=DARK_FG, selectcolor=FIELD_BG, activebackground=DARK_BG, activeforeground=DARK_FG)
    except Exception:
        pass

def set_dark_theme(widget):
    # Aplicar recursivamente el tema a todos los elementos
    _style_ttk()
    # Colorear este widget
    _theme_tk_widget(widget)
    # Recursar a los hijos
    for child in widget.winfo_children():
        _theme_tk_widget(child)
        set_dark_theme(child) 

def apply_dark_theme(target=None):
    if target is None:
        target = root
    set_dark_theme(target)

# Base de Datos
def _get_conn():
    conn = sqlite3.connect(DB_PATH, timeout=30, isolation_level=None)
    conn.execute("PRAGMA journal_mode=WAL;")     
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("PRAGMA busy_timeout=5000;")    
    conn.execute("PRAGMA synchronous=NORMAL;")   
    return conn

def _validar_fecha_iso(fecha_str: str) -> bool:
    from datetime import datetime
    try:
        datetime.strptime(fecha_str.strip(), "%Y-%m-%d")
        return True
    except Exception:
        return False

def _normalize_raza_input(text: str | None) -> str:
    # Minusculas, remover caracteres especiales
    if not text:
        return ""
    # Acentos
    txt = unicodedata.normalize("NFD", str(text))
    txt = "".join(ch for ch in txt if unicodedata.category(ch) != "Mn")
    # Minuscula
    txt = txt.lower()
    # Letras y espacios
    txt = re.sub(r"[^a-z\s]", " ", txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt

def _register_raza_combo(cb: ttk.Combobox):
    # Remover los ComboBox de Raza de la lista cuando se destruye el widget
    RAZA_COMBOS.append(cb)
    def _cleanup(_event=None, widget=cb):
        try:
            if widget in RAZA_COMBOS:
                RAZA_COMBOS.remove(widget)
        except Exception:
            pass
    cb.bind("<Destroy>", _cleanup)

def _load_raza_names(conn: sqlite3.Connection | None = None) -> list[str]:
    owns = False
    if conn is None:
        conn = _get_conn()
        owns = True
    rows = conn.execute("SELECT Nombre FROM Raza ORDER BY Nombre COLLATE NOCASE").fetchall()
    if owns: conn.close()
    return [r[0] for r in rows]

def _refresh_raza_options():
    # Cargar razas de la BD y actualizar ComboBox
    global RAZA_OPTIONS, RAZA_COMBOS
    RAZA_OPTIONS = _load_raza_names()
    values = RAZA_OPTIONS + [RAZA_SENTINEL]

    alive = []
    for cb in list(RAZA_COMBOS):
        try:
            if not cb.winfo_exists():
                continue
            cb.configure(values=values)
            alive.append(cb)
        except Exception:
            continue
    RAZA_COMBOS = alive

def _ensure_raza_exists(name: str) -> str:
    norm = _normalize_raza_input(name)
    if not norm:
        raise ValueError("La raza no puede estar vacía ni contener números/símbolos.")
    with _get_conn() as conn:
        conn.execute("BEGIN IMMEDIATE;")
        row = conn.execute(
            "SELECT RazaID, Nombre FROM Raza WHERE lower(Nombre)=?",
            (norm,)
        ).fetchone()
        if not row:
            conn.execute("INSERT INTO Raza (Nombre) VALUES (?)", (norm,))
            conn.commit()
            stored = norm
        else:
            stored = row[1]
    _refresh_raza_options()
    return stored


def _on_raza_selected(var: StringVar):
    # Handler de ComboBox Raza seleccionado
    if var.get() == RAZA_SENTINEL:
        new_name = simpledialog.askstring("Nueva raza", "Escribe la nueva raza:")
        if not new_name or not new_name.strip():
            var.set("")
            return
        try:
            stored = _ensure_raza_exists(new_name.strip())
            var.set(stored)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar la raza:\n{e}")
            var.set("")

def _get_raza_id(conn: sqlite3.Connection, raza_nombre: str) -> int:
    # Busca la raza por nombre (case-insensitive). Lanza ValueError si no existe
    norm = _normalize_raza_input(raza_nombre)
    if not norm:
        raise ValueError("La raza es obligatoria.")
    cur = conn.execute(
        "SELECT RazaID FROM Raza WHERE lower(Nombre) = lower(?)",
        (raza_nombre.strip(),)
    )
    row = cur.fetchone()
    if not row:
        raise ValueError(
            f"Raza '{raza_nombre}' no existe en el catálogo. "
        )
    return row[0]

def _canon(name: str | None) -> str:
    if name is None:
        return ""
    # strip + colapsar espacios
    return " ".join(str(name).strip().split()).lower()

def _fetch_ciudad(conn: sqlite3.Connection, ciudad: str) -> dict | None:
    # Buscar ciudad en BD
    conn.row_factory = sqlite3.Row
    
    row = conn.execute(
        "SELECT * FROM Ciudades WHERE lower(trim(Ciudad)) = ? LIMIT 1",
        (_canon(ciudad),)
    ).fetchone()
    if row:
        return dict(row)

    cur = conn.execute("SELECT * FROM Ciudades")
    for r in cur:
        if _canon(r["Ciudad"]) == _canon(ciudad):
            return dict(r)
    return None

def _fetch_segment_from_table(conn: sqlite3.Connection, table: str, origen: str, destino: str) -> dict | None:
   # Busca segmentos en Resumen y Rutas
    conn.row_factory = sqlite3.Row
    o, d = _canon(origen), _canon(destino)

    sql = f"""
        SELECT * FROM {table}
        WHERE lower(trim(Origen)) = ? AND lower(trim(Destino)) = ?
        LIMIT 1
    """
    row = conn.execute(sql, (o, d)).fetchone()
    if row:
        return dict(row)

    sql2 = f"SELECT * FROM {table} WHERE lower(trim(Origen)) = ?"
    for r in conn.execute(sql2, (o,)):
        if _canon(r["Destino"]) == d:
            return dict(r)

    for r in conn.execute(f"SELECT * FROM {table}"):
        if _canon(r["Origen"]) == o and _canon(r["Destino"]) == d:
            return dict(r)

    return None

def _fetch_ruta_segment(conn: sqlite3.Connection, origen: str, destino: str) -> dict | None:
    return _fetch_segment_from_table(conn, "Rutas", origen, destino)

def _fetch_resumen_segment(conn: sqlite3.Connection, origen: str, destino: str) -> dict | None:
    return _fetch_segment_from_table(conn, "Resumen", origen, destino)

def _tipo_from_char(t: str | None, conn: sqlite3.Connection, origen: str, destino: str) -> str:
    # N/I a Local/Internacional
    if t:
        tt = _canon(t).upper()
        if tt == "I":
            return "Internacional"
        if tt == "N":
            return "Local"
    # Inferir si no se encuentra
    co = _fetch_ciudad(conn, origen)
    cd = _fetch_ciudad(conn, destino)
    if co and cd and _canon(co.get("Pais")) != _canon(cd.get("Pais")):
        return "Internacional"
    return "Local"

def _generate_unique_pnr(conn: sqlite3.Connection, length: int = 6) -> str:
    alphabet = string.ascii_uppercase + string.digits
    while True:
        code = "".join(random.choice(alphabet) for _ in range(length))
        cur = conn.execute("SELECT 1 FROM Reserva WHERE CodigoPNR = ?", (code,))
        if cur.fetchone() is None:
            return code
        
def _ensure_vuelo_columns_from_rutas(conn: sqlite3.Connection):
    cols = {row[1] for row in conn.execute("PRAGMA table_info(Vuelo)")}
    ddl = []
    
    if "DistanciaKm" not in cols:    ddl.append("ALTER TABLE Vuelo ADD COLUMN DistanciaKm REAL;")
    if "TiempoHrs" not in cols:      ddl.append("ALTER TABLE Vuelo ADD COLUMN TiempoHrs REAL;")
    if "Costo" not in cols:          ddl.append("ALTER TABLE Vuelo ADD COLUMN Costo REAL;")
    
    if "TiempoVueloHrs" not in cols: ddl.append("ALTER TABLE Vuelo ADD COLUMN TiempoVueloHrs REAL;")
    if "TiempoEsperaHrs" not in cols:ddl.append("ALTER TABLE Vuelo ADD COLUMN TiempoEsperaHrs REAL;")
    if "CuotaAeropuerto" not in cols:ddl.append("ALTER TABLE Vuelo ADD COLUMN CuotaAeropuerto REAL;")
    if "Impuesto" not in cols:       ddl.append("ALTER TABLE Vuelo ADD COLUMN Impuesto REAL;")
    if "TiempoAduanaHrs" not in cols:ddl.append("ALTER TABLE Vuelo ADD COLUMN TiempoAduanaHrs REAL;")
    if "TiempoTotalHrs" not in cols: ddl.append("ALTER TABLE Vuelo ADD COLUMN TiempoTotalHrs REAL;")
    if "Descuento" not in cols:      ddl.append("ALTER TABLE Vuelo ADD COLUMN Descuento REAL;")
    if "CostoVuelo" not in cols:     ddl.append("ALTER TABLE Vuelo ADD COLUMN CostoVuelo REAL;")
    if "CostoTotal" not in cols:     ddl.append("ALTER TABLE Vuelo ADD COLUMN CostoTotal REAL;")
    for q in ddl:
        conn.execute(q)

# Generadores
_PLANE_TYPES = ["Nimbus2000"]
_SEAT_LETTERS = "ABCDEF"
_GATE_LETTERS = "ABCDEFGHJK"

def _rand_avion() -> str:
    return random.choice(_PLANE_TYPES)

def _rand_sala() -> str:
    return f"SALA-{random.randint(1, 15)}"

def _rand_puerta() -> str:
    return f"P-{random.randint(1, 40)}{random.choice(_GATE_LETTERS)}"

def _rand_asiento() -> str:
    return f"{random.randint(1, 35)}{random.choice(_SEAT_LETTERS)}"


def _insertar_usuario(
    nombre: str,
    ap_paterno: str,
    ap_materno: str | None,
    fecha_nac: str,
    nacionalidad: str,
    raza_nombre: str,
    correo: str,
    celular: str,
    conn: sqlite3.Connection | None = None,
) -> int:
    # Inserta en Usuarios y regresa el UsuarioID (PK). Lanza ValueError/IntegrityError con mensajes claros
    if not nombre or not nombre.strip():
        raise ValueError("El nombre es obligatorio.")
    if not ap_paterno or not ap_paterno.strip():
        raise ValueError("El apellido paterno es obligatorio.")
    if not fecha_nac or not _validar_fecha_iso(fecha_nac):
        raise ValueError("La fecha de nacimiento debe estar en formato ISO 'YYYY-MM-DD'.")
    if not correo:
        raise ValueError("El correo electrónico es obligatorio.")
    if not email_pattern.fullmatch(correo):
        raise ValueError("Correo electrónico inválido.")
    if not celular:
        raise ValueError("El número de celular es obligatorio.")
    if not phone_pattern.fullmatch(celular):
        raise ValueError("Número de celular inválido.")
    if not nacionalidad:
        raise ValueError("La nacionalidad es obligatoria.")

    owns_conn = False
    if conn is None:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON;")
        owns_conn = True

    try:
        raza_id = _get_raza_id(conn, raza_nombre)

        ap_materno  = ap_materno.strip()   if ap_materno  and ap_materno.strip()  else None
        correo      = correo.strip()       if correo      and correo.strip()      else None
        celular     = celular.strip()      if celular     and celular.strip()     else None

        cur = conn.execute(
            """
            INSERT INTO Usuarios
              (Nombre, ApPaterno, ApMaterno, FechaDeNacimiento, Nacionalidad, RazaID, Correo, Celular)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (nombre.strip(), ap_paterno.strip(), ap_materno, fecha_nac.strip(),
             nacionalidad, raza_id, correo, celular)
        )
        return cur.lastrowid
    finally:
        if owns_conn:
            conn.commit()
            conn.close()

def _crear_vuelos_desde_ruta(conn: sqlite3.Connection, path: list[str], fecha_vuelo: str) -> list[int]:
    # Crea Vuelo por par en Paths calculadas usando la tabla Rutas, 
    # usa Resumen si Rutas no está completo. Airport obtenido de tabla Ciudades

    vuelo_ids: list[int] = []

    for seg_idx in range(len(path)-1):
        o = path[seg_idx]
        d = path[seg_idx+1]

        row_rutas = _fetch_ruta_segment(conn, o, d)
        row_resum = None if row_rutas else _fetch_resumen_segment(conn, o, d)

        if not row_rutas and not row_resum:
            raise ValueError(f"No hay métricas para el tramo {o} -> {d} en Rutas ni Resumen.")

        if row_rutas:
            tipo_char       = row_rutas.get("Tipo Viaje")
            distancia_km    = row_rutas.get("Distancia (Km)")
            tiempo_vuelo    = row_rutas.get("Tiempo vuelo")
            costo_vuelo     = row_rutas.get("Costo vuelo")
            tiempo_espera   = row_rutas.get("Tiempo espera")
            cuota_aerop     = row_rutas.get("Cuota Aeropuerto")
            impuesto        = row_rutas.get("Impuesto")
            tiempo_aduana   = row_rutas.get("Tiempo Aduana")
            tiempo_total    = row_rutas.get("Tiempo total (Hrs)")
            descuento       = row_rutas.get("Descuento")
            costo_total     = row_rutas.get("Costo total")
        else:
            tipo_char       = row_resum.get("Tipo Viaje")
            distancia_km    = row_resum.get("Distancia (Km)")
            tiempo_vuelo    = row_resum.get("Tiempo total (Hrs)")  
            costo_vuelo     = None
            tiempo_espera   = None
            cuota_aerop     = None
            impuesto        = None
            tiempo_aduana   = None
            tiempo_total    = row_resum.get("Tiempo total (Hrs)")
            descuento       = None
            costo_total     = row_resum.get("Costo total")

        tipo_text = _tipo_from_char(tipo_char, conn, o, d)
        ciu_o = _fetch_ciudad(conn, o)
        aeropuerto_salida = ciu_o.get("Aeropuerto") if ciu_o else None

        vuelo_id = _crear_vuelo(
            conn,
            origen=o, destino=d, fecha=fecha_vuelo, tipo=tipo_text,
            aeropuerto=aeropuerto_salida, avion=None, sala=None, puerta=None,
            distancia_km=distancia_km, tiempo_hrs=tiempo_vuelo, costo=costo_vuelo,
            tiempo_vuelo_hrs=tiempo_vuelo,
            tiempo_espera_hrs=tiempo_espera,
            cuota_aeropuerto=cuota_aerop,
            impuesto=impuesto,
            tiempo_aduana_hrs=tiempo_aduana,
            tiempo_total_hrs=tiempo_total,
            descuento=descuento,
            costo_total=costo_total
        )
        vuelo_ids.append(vuelo_id)

    return vuelo_ids

def _crear_reserva(conn: sqlite3.Connection, titular_id: int | None,
                   contacto_email: str | None, contacto_tel: str | None) -> tuple[int,str]:
    pnr = _generate_unique_pnr(conn)
    contacto_email = contacto_email.strip() if contacto_email else None
    contacto_tel   = contacto_tel.strip()   if contacto_tel   else None
    cur = conn.execute(
        """
        INSERT INTO Reserva (CodigoPNR, TitularID, ContactoEmail, ContactoTelefono, Estado)
        VALUES (?, ?, ?, ?, 'confirmada')
        """,
        (pnr, titular_id, contacto_email, contacto_tel)
    )
    return cur.lastrowid, pnr

def _crear_vuelo(conn: sqlite3.Connection, *,
                 origen: str, destino: str, fecha: str,
                 tipo: str = "Local",
                 aeropuerto: str | None = None,
                 avion: str | None = None,
                 sala: str | None = None,
                 puerta: str | None = None,
                 distancia_km: float | None = None,
                 tiempo_hrs: float | None = None,   
                 costo: float | None = None,        
                 tiempo_vuelo_hrs: float | None = None,
                 tiempo_espera_hrs: float | None = None,
                 cuota_aeropuerto: float | None = None,
                 impuesto: float | None = None,
                 tiempo_aduana_hrs: float | None = None,
                 tiempo_total_hrs: float | None = None,
                 descuento: float | None = None,
                 costo_total: float | None = None,
                 costo_vuelo: float | None = None   
                 ) -> int:
    if not fecha or (len(fecha) not in (10,19)):
        raise ValueError("La fecha del vuelo debe ser 'YYYY-MM-DD' o 'YYYY-MM-DD HH:MM:SS'.")

    _ensure_vuelo_columns_from_rutas(conn)

    if tiempo_vuelo_hrs is not None and tiempo_hrs is None:
        tiempo_hrs = tiempo_vuelo_hrs
    if costo_vuelo is None and costo is not None:
        costo_vuelo = costo
    if costo is None and costo_vuelo is not None:
        costo = costo_vuelo
    if costo_total is None and costo is not None:
        costo_total = costo

    if avion is None:  avion = _rand_avion()
    if sala is None:   sala  = _rand_sala()
    if puerta is None: puerta = _rand_puerta()

    cur = conn.execute(
        """
        INSERT INTO Vuelo
        (Origen, Destino, Fecha, Tipo, Aeropuerto, Avion, SalaEspera, PuertaEmbarque,
         DistanciaKm, TiempoHrs, Costo,
         TiempoVueloHrs, TiempoEsperaHrs, CuotaAeropuerto, Impuesto, TiempoAduanaHrs,
         TiempoTotalHrs, Descuento, CostoVuelo, CostoTotal)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        (origen, destino, fecha, tipo, aeropuerto, avion, sala, puerta,
         distancia_km, tiempo_hrs, costo,
         tiempo_vuelo_hrs, tiempo_espera_hrs, cuota_aeropuerto, impuesto, tiempo_aduana_hrs,
         tiempo_total_hrs, descuento, costo_vuelo, costo_total)
    )
    return cur.lastrowid



def _agregar_reserva_pasajero(conn: sqlite3.Connection, reserva_id: int, usuario_id: int, rol: str, asiento: str | None = None):
    if not asiento:
        asiento = _rand_asiento()
    conn.execute(
        "INSERT INTO ReservaPasajero (ReservaID, UsuarioID, Rol, Asiento) VALUES (?,?,?,?)",
        (reserva_id, usuario_id, rol, asiento)
    )
    return asiento

def _agregar_reserva_vuelo(conn: sqlite3.Connection, reserva_id: int, vuelo_id: int, segmento: int, clase_tarifa: str | None = None):
    conn.execute(
        "INSERT INTO ReservaVuelo (ReservaID, VueloID, Segmento, ClaseTarifa) VALUES (?,?,?,?)",
        (reserva_id, vuelo_id, segmento, clase_tarifa)
    )

def _get_selected_route_dict():
    val = ruta_var.get()
    if val == 1:
        return LAST_ROUTES.get("costo")
    elif val == 2:
        return LAST_ROUTES.get("distancia")
    elif val == 3:
        return LAST_ROUTES.get("tiempo")
    return None

### Generar Ticket

def _get_conn_ro():
    uri = f"file:{DB_PATH}?mode=ro"
    conn = sqlite3.connect(uri, uri=True, timeout=10, isolation_level=None)
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.row_factory = sqlite3.Row
    return conn

def _coalesce(*vals):
    for v in vals:
        if v is not None:
            return v
    return None

def _fetch_ticket_data(reserva_id: int):
    # Obtener todos los datos del ticket como diccionarios
    with _get_conn_ro() as conn:
        conn.row_factory = sqlite3.Row

        r = conn.execute("SELECT * FROM Reserva WHERE ReservaID=?", (reserva_id,)).fetchone()
        if not r:
            raise ValueError(f"Reserva {reserva_id} no existe.")
        r = dict(r) 

        pax = conn.execute("""
            SELECT U.UsuarioID, U.Nombre, U.ApPaterno, U.ApMaterno, U.FechaDeNacimiento,
                   U.Nacionalidad, Rz.Nombre AS Raza, RP.Rol, RP.Asiento
            FROM ReservaPasajero RP
            JOIN Usuarios U ON U.UsuarioID = RP.UsuarioID
            LEFT JOIN Raza Rz ON Rz.RazaID = U.RazaID
            WHERE RP.ReservaID=?
            ORDER BY CASE RP.Rol WHEN 'titular' THEN 0 WHEN 'pasajero' THEN 1 ELSE 2 END,
                     U.ApPaterno, U.Nombre
        """, (reserva_id,)).fetchall()
        pax = [dict(p) for p in pax]  

        segs = conn.execute("""
            SELECT RV.Segmento, V.*
            FROM ReservaVuelo RV
            JOIN Vuelo V ON V.VueloID = RV.VueloID
            WHERE RV.ReservaID=?
            ORDER BY RV.Segmento
        """, (reserva_id,)).fetchall()
        segs = [dict(s) for s in segs]  

        return dict(reserva=r, pasajeros=pax, segmentos=segs)


def _calc_itinerary_totals(segmentos):
    # Sumar cantidades de la ruta (no multiplicadas por pasajeros)
    total_dist = 0.0
    total_hrs  = 0.0
    total_cost_per_pax = 0.0
    for s in segmentos:
        dist = s["DistanciaKm"]
        
        hrs  = _coalesce(s["TiempoTotalHrs"], s["TiempoHrs"], 0.0)
        
        ctot = _coalesce(
            s["CostoTotal"],
            (_coalesce(s["Costo"], 0.0)
             + _coalesce(s["CuotaAeropuerto"], 0.0)
             + _coalesce(s["Impuesto"], 0.0)
             - _coalesce(s["Descuento"], 0.0))
        )
        total_dist += float(dist or 0.0)
        total_hrs  += float(hrs or 0.0)
        total_cost_per_pax += float(ctot or 0.0)
    return total_dist, total_hrs, total_cost_per_pax

def guardar_ticket_pdf(reserva_id: int):
    try:
        from reportlab.lib.pagesizes import LETTER
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
        from xml.sax.saxutils import escape
        from reportlab.lib.styles import ParagraphStyle
    except ImportError:
        messagebox.showerror(
            "Falta dependencia",
            "No se encontró ReportLab.\nInstálalo con:\n\npip install reportlab"
        )
        return

    try:
        data = _fetch_ticket_data(reserva_id)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo obtener la información de la reserva:\n{e}")
        return

    r   = data["reserva"]
    pax = data["pasajeros"]
    segs= data["segmentos"]

    if not segs:
        messagebox.showerror("Sin segmentos", "La reserva no tiene vuelos asociados.")
        return

    # Totales
    total_dist, total_hrs, total_cost_per_pax = _calc_itinerary_totals(segs)
    pax_count = len(pax)
    grand_total = total_cost_per_pax * pax_count

    # Diálogo para elegir nombre/ubicación del PDF
    default_name = f"Ticket_{r['CodigoPNR']}.pdf"
    out_path = filedialog.asksaveasfilename(
        title="Guardar ticket en PDF",
        defaultextension=".pdf",
        initialfile=default_name,
        filetypes=[("PDF", "*.pdf")]
    )
    if not out_path:
        return

    styles = getSampleStyleSheet()
    title  = styles["Title"]
    h2     = styles["Heading2"]
    h3     = styles["Heading3"]
    body   = styles["BodyText"]

    doc = SimpleDocTemplate(out_path, pagesize=LETTER,
                            rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []

    # Encabezado
    story.append(Paragraph("AeroIbero – Ticket / Itinerario", title))
    story.append(Paragraph(f"PNR: {r['CodigoPNR']}", h2))
    story.append(Spacer(1, 8))

    # Datos de reserva
    story.append(Paragraph("Resumen de reserva", h3))
    res_tbl = [
        ["PNR", r["CodigoPNR"]],
        ["Estado", r["Estado"]],
        ["Fecha creación", r["FechaCreacion"]],
        ["Contacto email", r.get("ContactoEmail","") or "-"],
        ["Contacto teléfono", r.get("ContactoTelefono","") or "-"],
        ["Pasajeros", str(pax_count)],
    ]
    t = Table(res_tbl, hAlign="LEFT", colWidths=[140, 380])
    t.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.whitesmoke),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    # Pasajeros
    story.append(Paragraph("Pasajeros", h3))
    pax_header = ["ID", "Nombre completo", "Fecha nac.", "Nacionalidad", "Raza", "Rol", "Asiento"]
    pax_rows = []
    for p in pax:
        full = " ".join([p["Nombre"] or "", p["ApPaterno"] or "", p["ApMaterno"] or ""]).strip()
        pax_rows.append([
            p["UsuarioID"], full, p["FechaDeNacimiento"] or "",
            p["Nacionalidad"] or "", p["Raza"] or "", p["Rol"] or "", p["Asiento"] or ""
        ])
    pax_tbl = Table([pax_header] + pax_rows, hAlign="LEFT", colWidths=[40, 180, 70, 80, 70, 60, 50])
    pax_tbl.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#f0f0f0")),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(pax_tbl)
    story.append(Spacer(1, 10))

    # Segmentos – imprimimos info + métricas + costos para cada uno
    story.append(Paragraph("Segmentos", h3))
    for s in segs:
        seg_title = f"Segmento {s['Segmento']}: {s['Origen']} → {s['Destino']}  ({s['Fecha']})"
        story.append(Paragraph(seg_title, styles["Heading4"]))

        info_tbl = [
            ["Tipo", s["Tipo"]],
            ["Aeropuerto", s.get("Aeropuerto","") or "-"],
            ["Avión", s.get("Avion","") or "-"],
            ["Sala de espera", s.get("SalaEspera","") or "-"],
            ["Puerta", s.get("PuertaEmbarque","") or "-"],
        ]
        t_info = Table(info_tbl, hAlign="LEFT", colWidths=[120, 400])
        t_info.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.25,colors.grey)]))
        story.append(t_info)
        story.append(Spacer(1, 4))

        metrics_tbl = [
            ["Distancia (Km)", s.get("DistanciaKm")],
            ["Tiempo vuelo (h)", _coalesce(s.get("TiempoVueloHrs"), s.get("TiempoHrs"))],
            ["Tiempo espera (h)", s.get("TiempoEsperaHrs")],
            ["Tiempo aduana (h)", s.get("TiempoAduanaHrs")],
            ["Tiempo total (h)", _coalesce(s.get("TiempoTotalHrs"), s.get("TiempoHrs"))],
        ]
        t_met = Table(metrics_tbl, hAlign="LEFT", colWidths=[160, 360])
        t_met.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.25,colors.grey)]))
        story.append(t_met)
        story.append(Spacer(1, 4))

        costs_tbl = [
            ["Costo vuelo", s.get("CostoVuelo")],
            ["Cuota aeropuerto", s.get("CuotaAeropuerto")],
            ["Impuesto", s.get("Impuesto")],
            ["Descuento", s.get("Descuento")],
            ["Costo total", _coalesce(s.get("CostoTotal"), s.get("Costo"))],
        ]
        t_cost = Table(costs_tbl, hAlign="LEFT", colWidths=[160, 360])
        t_cost.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.25,colors.grey)]))
        story.append(t_cost)
        story.append(Spacer(1, 10))

    # Totales de itinerario y de reserva
    story.append(Paragraph("Totales del itinerario", h3))
    tot_tbl = [
        ["Distancia total (Km)", f"{total_dist:.1f}"],
        ["Tiempo total (h)",    f"{total_hrs:.2f}"],
        ["Costo por pasajero",  f"${total_cost_per_pax:,.2f}"],
        ["Pasajeros",           str(pax_count)],
        ["Costo total (x pasajeros)", f"${grand_total:,.2f}"],
    ]
    t_tot = Table(tot_tbl, hAlign="LEFT", colWidths=[200, 320])
    t_tot.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),0.25,colors.grey),
        ("BACKGROUND",(0,0),(-1,0),colors.whitesmoke)
    ]))
    story.append(t_tot)

    try:
        doc.build(story)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el PDF:\n{e}")
        return

    messagebox.showinfo("Listo", f"Ticket guardado en:\n{out_path}")

# guardar

def guardarDatos():
    # 1) Datos UI
    origen = origen_var.get()
    destino = destino_var.get()
    fecha_vuelo = fecha_entry.get()

    nombre    = nombre_entry.get()
    apellidoP = apellidoP_entry.get()
    apellidoM = apellidoM_entry.get()
    fechaN    = fechaN_entry.get()
    nacionalidad = nacionalidad_var.get()
    raza      = raza_var.get()
    correo    = correo_entry.get()
    telefono  = telefono_entry.get()
    extras    = extras_entry.get()

    # 2) Validar ruta y fecha
    ruta_sel = _get_selected_route_dict()
    if not ruta_sel or not ruta_sel.get("path"):
        messagebox.showerror("Ruta no seleccionada", "Elige una ruta (Precio/Distancia/Tiempo) antes de registrar.")
        return
    if not fecha_vuelo or len(fecha_vuelo) not in (10, 19):
        messagebox.showerror("Fecha inválida", "Captura la fecha del vuelo en 'YYYY-MM-DD' o 'YYYY-MM-DD HH:MM:SS'.")
        return

    # 3) Una sola conexión + transacción
    conn = None
    try:
        conn = _get_conn()
        conn.execute("BEGIN IMMEDIATE;")

        # 4) Titular
        titular_id = _insertar_usuario(
            nombre=nombre, ap_paterno=apellidoP, ap_materno=apellidoM,
            fecha_nac=fechaN, nacionalidad=nacionalidad, raza_nombre=raza,
            correo=correo, celular=telefono, conn=conn
        )

        # 5) Reserva + PNR
        reserva_id, pnr = _crear_reserva(conn, titular_id, contacto_email=correo, contacto_tel=telefono)

        # 6) Titular -> Reserva
        _agregar_reserva_pasajero(conn, reserva_id, titular_id, rol="titular")

        # 7) Vuelos reales + liga
        path = ruta_sel["path"]
        vuelo_ids = _crear_vuelos_desde_ruta(conn, path, fecha_vuelo)
        for i, vid in enumerate(vuelo_ids, start=1):
            _agregar_reserva_vuelo(conn, reserva_id, vid, segmento=i, clase_tarifa=None)

        conn.commit()
    except sqlite3.IntegrityError as ie:
        if conn: conn.rollback()
        msg = str(ie)
        if "Usuarios.Correo" in msg:
            messagebox.showerror("Registro fallido", "El correo ya está registrado.")
        elif "Usuarios.Celular" in msg:
            messagebox.showerror("Registro fallido", "El celular ya está registrado.")
        else:
            messagebox.showerror("Registro fallido", f"Error de integridad:\n{msg}")
        return
    except ValueError as ve:
        if conn: conn.rollback()
        messagebox.showerror("Datos inválidos", str(ve))
        return
    except Exception as e:
        if conn: conn.rollback()
        messagebox.showerror("Error", f"No se pudo completar el registro:\n{e}")
        return
    finally:
        if conn: conn.close()

    # 9) Acompañantes
    try:
        extras_num = int(extras)
    except Exception:
        extras_num = 0
    if extras_num >= 1:
        registroExtras(reserva_id)

    # 10) Ventana resumen
    ventana2 = Toplevel(root)
    ventana2.title(f'Reserva creada – PNR {pnr}')
    ventana2.resizable(False, False)

    frame_ventana2 = Frame(ventana2, padx=10, pady=10, relief=GROOVE, borderwidth=2)
    frame_ventana2.pack(padx=10, pady=10, fill='x')
    frame_ventana2.grid_columnconfigure(0, weight=1)
    frame_ventana2.grid_columnconfigure(1, weight=0)

    Label(frame_ventana2, text='Datos Reservación', font=('Arial', 12, 'bold'))\
        .grid(row=0, column=0, columnspan=2, pady=(0,10), sticky='w')

    btn_pdf = Button(
        frame_ventana2, text="Guardar ticket PDF",
        font=('Arial', 11, 'bold'), bg='#4CAF50', fg='white',
        command=lambda: guardar_ticket_pdf(reserva_id)
    )
    btn_pdf.grid(row=0, column=1, padx=(8,0), pady=(0,10), sticky='e')

    Label(frame_ventana2, text=f'PNR: {pnr}').grid(row=1, column=0, padx=5, pady=2, sticky='w')
    Label(frame_ventana2, text=f'Origen: {origen}').grid(row=2, column=0, padx=5, pady=2, sticky='w')
    Label(frame_ventana2, text=f'Destino: {destino}').grid(row=3, column=0, padx=5, pady=2, sticky='w')
    Label(frame_ventana2, text=f'Fecha vuelo: {fecha_vuelo}').grid(row=4, column=0, padx=5, pady=2, sticky='w')

    Label(frame_ventana2, text='Datos Usuario (Titular)', font=('Arial', 12, 'bold'))\
        .grid(row=5, column=0, columnspan=2, pady=(10,10), sticky='w')
    Label(frame_ventana2, text=f'ID: {titular_id}').grid(row=6, column=0, padx=5, pady=2, sticky='w')
    Label(frame_ventana2, text=f'Nombre: {nombre} {apellidoP} {apellidoM}')\
        .grid(row=7, column=0, padx=5, pady=2, sticky='w')
    Label(frame_ventana2, text=f'Nacionalidad: {nacionalidad}').grid(row=8, column=0, padx=5, pady=2, sticky='w')
    Label(frame_ventana2, text=f'Raza: {raza}').grid(row=9, column=0, padx=5, pady=2, sticky='w')
    Label(frame_ventana2, text=f'Correo: {correo}').grid(row=10, column=0, padx=5, pady=2, sticky='w')
    Label(frame_ventana2, text=f'Celular: {telefono}').grid(row=11, column=0, padx=5, pady=2, sticky='w')

    resLabel = rutaToLabel(ruta_sel)
    Label(frame_ventana2, text='Ruta Elegida', font=('Arial', 12, 'bold'))\
        .grid(row=12, column=0, columnspan=2, pady=(10,10), sticky='w')
    Label(frame_ventana2, text=resLabel, justify="left", wraplength=600)\
        .grid(row=13, column=0, columnspan=2, padx=5, pady=2, sticky='w')
    
    try:
        set_dark_theme(ventana2)
    except Exception:
        pass

def registroExtras(reserva_id: int):
    try:
        extras = int(extras_entry.get())
    except Exception:
        extras = 0

    for n in range(1, extras + 1):
        ventana3 = Toplevel(root)
        ventana3.title(f'Datos Acompañante {n} 🙋')
        ventana3.resizable(False, False)
        ventana3.transient(root)         
        ventana3.grab_set()              

        frame_ventana3 = Frame(ventana3, padx=10, pady=10, relief=GROOVE, borderwidth=2)
        frame_ventana3.pack(padx=10, pady=10, fill='x')
        frame_ventana3.columnconfigure(0, weight=1)

        Label(frame_ventana3, text=f'Datos Acompañante {n}', font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0, 10))

        Label(frame_ventana3, text='Nombre:').grid(row=1, column=0, sticky='e', padx=5, pady=2)
        nombreE_entry = Entry(frame_ventana3); nombreE_entry.grid(row=1, column=1, padx=5, pady=2)

        Label(frame_ventana3, text='Apellido Paterno:').grid(row=2, column=0, sticky='e', padx=5, pady=2)
        apellidoPE_entry = Entry(frame_ventana3); apellidoPE_entry.grid(row=2, column=1, padx=5, pady=2)

        Label(frame_ventana3, text='Apellido Materno:').grid(row=3, column=0, sticky='e', padx=5, pady=2)
        apellidoME_entry = Entry(frame_ventana3); apellidoME_entry.grid(row=3, column=1, padx=5, pady=2)

        Label(frame_ventana3, text='Fecha de Nacimiento:').grid(row=4, column=0, sticky='e', padx=5, pady=2)
        fechaNE_entry = Entry(frame_ventana3); fechaNE_entry.grid(row=4, column=1, padx=5, pady=2)

        Label(frame_ventana3, text='Nacionalidad:').grid(row=5, column=0, sticky='e', padx=5, pady=2)
        nacionalidadE_var = StringVar()
        nacionalidadE_combo = ttk.Combobox(
            frame_ventana3, textvariable=nacionalidadE_var,
            values=["mediaterrano", "narniano", "ozniano"], state="readonly"
        )
        nacionalidadE_combo.grid(row=5, column=1, padx=5, pady=2, sticky='we')
        nacionalidadE_combo.set("")

        Label(frame_ventana3, text='Raza:').grid(row=6, column=0, sticky='e', padx=5, pady=2)
        razaE_var = StringVar()
        razaE_combo = ttk.Combobox(frame_ventana3, textvariable=razaE_var, state="readonly")
        _register_raza_combo(razaE_combo)
        _refresh_raza_options()
        razaE_combo.grid(row=6, column=1, padx=5, pady=2, sticky='we')
        razaE_combo.set("")
        razaE_combo.bind("<<ComboboxSelected>>", lambda e, v=razaE_var: _on_raza_selected(v))


        Label(frame_ventana3, text='Correo:').grid(row=7, column=0, sticky='e', padx=5, pady=2)
        correoE_entry = Entry(frame_ventana3); correoE_entry.grid(row=7, column=1, padx=5, pady=2)

        Label(frame_ventana3, text='Celular:').grid(row=8, column=0, sticky='e', padx=5, pady=2)
        telefonoE_entry = Entry(frame_ventana3); telefonoE_entry.grid(row=8, column=1, padx=5, pady=2)

        id_var = StringVar(); id_var.set("ID Cliente:")
        Label(frame_ventana3, textvariable=id_var).grid(row=9, column=0, columnspan=2, padx=5, pady=2)

        Label(frame_ventana3, text="⚠️ Debes registrar para continuar", fg="red", font=("Arial", 9, "italic"))\
            .grid(row=10, column=0, columnspan=2, pady=(10,5))

        registroE_button = Button(ventana3, text='Registrar', font=('Arial', 11, 'bold'),
                                  bg='#4CAF50', fg='white')
        registroE_button.pack(pady=15)

        try:
            apply_dark_theme(ventana3)
        except Exception:
            pass
        
        registered = False
        def _on_close():
            if not registered:
                messagebox.showwarning("Registro requerido", "Debes presionar 'Registrar' para continuar.")
                ventana3.lift(); ventana3.focus_force()
                return
            ventana3.destroy()

        ventana3.protocol("WM_DELETE_WINDOW", _on_close)
        ventana3.bind("<Escape>", lambda e: _on_close())  

        def registrar():
            nonlocal registered
            try:
                with _get_conn() as connE:
                    connE.execute("BEGIN IMMEDIATE;")
                    user_id = _insertar_usuario(
                        nombre=nombreE_entry.get(),
                        ap_paterno=apellidoPE_entry.get(),
                        ap_materno=apellidoME_entry.get(),
                        fecha_nac=fechaNE_entry.get(),
                        nacionalidad=nacionalidadE_var.get(),
                        raza_nombre=_normalize_raza_input(razaE_var.get()),
                        correo=correoE_entry.get(),
                        celular=telefonoE_entry.get(),
                        conn=connE
                    )
                    _agregar_reserva_pasajero(connE, reserva_id, user_id, rol="pasajero")
                    connE.commit()
                id_var.set(f'ID Cliente: {user_id}')
                registered = True
                registroE_button.config(state="disabled", text="Registrado")
                messagebox.showinfo("Acompañante registrado", f"Se agregó el usuario {user_id} a la reserva.")
                ventana3.grab_release()
                ventana3.destroy() 
            except sqlite3.IntegrityError as ie:
                msg = str(ie)
                if "Usuarios.Correo" in msg:
                    messagebox.showerror("Registro fallido", "El correo ya está registrado.")
                elif "Usuarios.Celular" in msg:
                    messagebox.showerror("Registro fallido", "El celular ya está registrado.")
                else:
                    messagebox.showerror("Registro fallido", f"Error de integridad:\n{msg}")
            except ValueError as ve:
                messagebox.showerror("Datos inválidos", str(ve))
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo registrar el acompañante:\n{e}")

        registroE_button.configure(command=registrar)

        ventana3.wait_window() 

def horasToHorasMinutos(horas_dec):
    if horas_dec is None:
        return None, None
    total_minutes = int(round(float(horas_dec) * 60))
    horas, minutos = divmod(total_minutes, 60)  
    return horas, minutos

def rutaToLabel(ruta):
    label = "Conexiones:\n"
    numCiudades = len(ruta['path'])
    conexiones = ruta['path']
    for i in range(numCiudades - 1):
        label = f"{label}\t{conexiones[i]} - {conexiones[i+1]}\n"
    totales = ruta['totals']
    costo = totales.get('costo')
    distancia = totales.get('distancia')
    tiempo = totales.get('tiempo')
    horas, minutos = horasToHorasMinutos(tiempo)
    label = f"{label}\nTotales:\n\t${costo}\n\t{distancia} km\n\t{horas}h {minutos}m"
    return label

def checarRutas(origen: str, destino: str):
    global LAST_ROUTES
    if destino != 'Selecciona destino' and origen != 'Selecciona origen' and origen and destino:
        rutas = [rutaCosto, rutaDistancia, rutaTiempo] = compRoutes.bestRoutes(origen, destino)
        hayRuta = all(r["path"] for r in rutas)

        if hayRuta:
            LAST_ROUTES["costo"]     = rutaCosto
            LAST_ROUTES["distancia"] = rutaDistancia
            LAST_ROUTES["tiempo"]    = rutaTiempo

            resCosto     = rutaToLabel(rutaCosto)
            resDistancia = rutaToLabel(rutaDistancia)
            resTiempo    = rutaToLabel(rutaTiempo)
        else:
            LAST_ROUTES = {"costo": None, "distancia": None, "tiempo": None}
            resCosto = resDistancia = resTiempo = f'No hay ruta {origen} - {destino}'
    else:
        LAST_ROUTES = {"costo": None, "distancia": None, "tiempo": None}
        resCosto = resDistancia = resTiempo = '-'

    reMinPrecio_label.config(text=resCosto)
    reMinDistancia_label.config(text=resDistancia)
    reMinTiempo_label.config(text=resTiempo)

class ScrollableFrame(Frame):
    def __init__(self, parent, *, height=520, bg="#222"):
        super().__init__(parent, bg=bg)
        self._bg = bg

        self.canvas = Canvas(self, borderwidth=0, highlightthickness=0, bg=bg)
        self.vscroll = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vscroll.set)

        self.vscroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.content = Frame(self.canvas, bg=bg)
        self._win = self.canvas.create_window((0, 0), window=self.content, anchor="nw")

        self.content.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        self.content.bind("<Enter>", self._bind_wheel)
        self.content.bind("<Leave>", self._unbind_wheel)

        try:
            set_dark_theme(self.content)
        except Exception:
            pass

    def _on_frame_configure(self, _):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self._win, width=event.width)

    def _bind_wheel(self, _):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)  # Win/Mac
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)    # Linux 1
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)    # Linux 2

    def _unbind_wheel(self, _):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-3, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(3, "units")
        else:
            self.canvas.yview_scroll(int(-event.delta/40), "units")



# ventana principal
WINDOW_W, WINDOW_H = 350, 800      
root = Tk()
root.resizable(True, True)
root.title('Formulario de Reservación ✈️')
root.geometry(f"{WINDOW_W}x{WINDOW_H}")  
root.minsize(350, 200)     

def on_origen_destino_change(*args):
    checarRutas(origen_var.get(), destino_var.get())

# frame vuelo
root_scroller = ScrollableFrame(root, height=800, bg="#222")
root_scroller.pack(fill='both', expand=True)

frame_vuelo = Frame(root_scroller.content, padx=10, pady=10, relief=GROOVE, borderwidth=2, bg="#222")
frame_vuelo.pack(padx=10, pady=10, fill='x')

datosVuelo_label = Label(frame_vuelo, text='Datos Vuelo', font=('Arial', 12, 'bold'), bg="#222", fg="#eee")
datosVuelo_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

frame_vuelo.grid_columnconfigure(1, weight=1)

city_list = getattr(graphs, "nodes", [])
if not city_list and hasattr(graphs, "get_nodes"):
    try:
        city_list = graphs.get_nodes()
    except Exception:
        city_list = []

# Origen
origen_label = Label(frame_vuelo, text='Origen:')
origen_label.grid(row=1, column=0, sticky='e', padx=5, pady=2)

origen_var = StringVar()
origen_combo = ttk.Combobox(frame_vuelo, textvariable=origen_var, values=city_list, state="readonly")
origen_combo.grid(row=1, column=1, padx=5, pady=2, sticky='we')
origen_combo.set("Selecciona origen") 

# Destino
destino_label = Label(frame_vuelo, text='Destino:')
destino_label.grid(row=2, column=0, sticky='e', padx=5, pady=2)

destino_var = StringVar()
destino_combo = ttk.Combobox(frame_vuelo, textvariable=destino_var, values=city_list, state="readonly")
destino_combo.grid(row=2, column=1, padx=5, pady=2, sticky='we')
destino_combo.set("Selecciona destino")  

# Fecha 
fecha_label = Label(frame_vuelo, text='Fecha:')
fecha_label.grid(row=3, column=0, sticky='we', padx=5, pady=2)
fecha_entry = Entry(frame_vuelo)
fecha_entry.grid(row=3, column=1, padx=5, pady=2, sticky='we')

def _trigger_update(*_):
    on_origen_destino_change()

origen_combo.bind("<<ComboboxSelected>>", lambda e: _trigger_update())
destino_combo.bind("<<ComboboxSelected>>", lambda e: _trigger_update())

def _on_origen_selected(e=None):
    sel = origen_var.get()
    new_vals = [c for c in city_list if c != sel]
    destino_combo["values"] = new_vals
    if destino_var.get() == sel:
        destino_var.set("")
    _trigger_update()

origen_combo.bind("<<ComboboxSelected>>", _on_origen_selected)

origen_var.trace_add("write", lambda *_: _trigger_update())
destino_var.trace_add("write", lambda *_: _trigger_update())


# frame rutas
frame_rutas = Frame(root_scroller.content, padx=10, pady=10, relief=GROOVE, borderwidth=2, bg="#222")
frame_rutas.pack(padx=10, pady=10, fill='x', expand=True)
frame_rutas.grid_columnconfigure(0, weight=1)
frame_rutas.grid_columnconfigure(1, weight=0)

rutas_label = Label(frame_rutas, text='Rutas', font=('Arial', 12, 'bold'), bg="#222", fg="#eee")
rutas_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))

ruta_var = IntVar(value=1)  # guarda cuál está seleccionado

minPrecio_label = Label(frame_rutas, text='Menor Precio', font=('Arial', 10, 'bold'))
minPrecio_label.grid(row=1, column=0, sticky='w', padx=5, pady=2)
reMinPrecio_label = Label(frame_rutas, text='-', justify="left")
reMinPrecio_label.grid(row=2, column=0, sticky='w', padx=5, pady=2)
minPrecio_radio = Radiobutton(frame_rutas, variable=ruta_var, value=1)
minPrecio_radio.grid(row=1, column=1, sticky='w', padx=5)

minDistancia_label = Label(frame_rutas, text='Menor Distancia', font=('Arial', 10, 'bold'))
minDistancia_label.grid(row=3, column=0, sticky='w', padx=5, pady=2)
reMinDistancia_label = Label(frame_rutas, text='-', justify="left")
reMinDistancia_label.grid(row=4, column=0, sticky='w', padx=5, pady=2)
minDistancia_radio = Radiobutton(frame_rutas, variable=ruta_var, value=2)
minDistancia_radio.grid(row=3, column=1, sticky='w',padx=5)

minTiempo_label = Label(frame_rutas, text='Menor Tiempo', font=('Arial', 10, 'bold'))
minTiempo_label.grid(row=5, column=0, sticky='w', padx=5, pady=2)
reMinTiempo_label = Label(frame_rutas, text='-', justify="left")
reMinTiempo_label.grid(row=6, column=0, sticky='w', padx=5, pady=2)
minTiempo_radio = Radiobutton(frame_rutas, variable=ruta_var, value=3)
minTiempo_radio.grid(row=5, column=1, sticky='w',padx=5)

# frame usuario
frame_usuario = Frame(root_scroller.content, padx=10, pady=10, relief=GROOVE, borderwidth=2, bg="#222")
frame_usuario.pack(padx=10, pady=10, fill='x')

datosUsuario_label = Label(frame_usuario, text='Datos Usuario', font=('Arial', 12, 'bold'), bg="#222", fg="#eee")
datosUsuario_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

nombre_label = Label(frame_usuario, text='Nombre:')
nombre_label.grid(row=1, column=0, sticky='e', padx=5, pady=2)
nombre_entry = Entry(frame_usuario)
nombre_entry.grid(row=1, column=1, padx=5, pady=2)

apellidoP_label = Label(frame_usuario, text='Apellido Paterno:')
apellidoP_label.grid(row=2, column=0, sticky='e', padx=5, pady=2)
apellidoP_entry = Entry(frame_usuario)
apellidoP_entry.grid(row=2, column=1, padx=5, pady=2)

apellidoM_label = Label(frame_usuario, text='Apellido Materno:')
apellidoM_label.grid(row=3, column=0, sticky='e', padx=5, pady=2)
apellidoM_entry = Entry(frame_usuario)
apellidoM_entry.grid(row=3, column=1, padx=5, pady=2)

fechaN_label = Label(frame_usuario, text='Fecha de Nacimiento:')
fechaN_label.grid(row=4, column=0, sticky='e', padx=5, pady=2)
fechaN_entry = Entry(frame_usuario)
fechaN_entry.grid(row=4, column=1, padx=5, pady=2)

nacionalidad_label = Label(frame_usuario, text='Nacionalidad:')
nacionalidad_label.grid(row=5, column=0, sticky='e', padx=5, pady=2)

nacionalidad_var = StringVar()
nacionalidad_combo = ttk.Combobox(
    frame_usuario,
    textvariable=nacionalidad_var,
    values=["mediaterrano", "narniano", "ozniano"],
    state="readonly"
)
nacionalidad_combo.grid(row=5, column=1, padx=5, pady=2, sticky='we')
nacionalidad_combo.set("")  # vacío por defecto, el usuario debe elegir


raza_label = Label(frame_usuario, text='Raza:')
raza_label.grid(row=6, column=0, sticky='e', padx=5, pady=2)
raza_var = StringVar()
raza_combo = ttk.Combobox(frame_usuario, textvariable=raza_var, state="readonly")
_register_raza_combo(raza_combo)
_refresh_raza_options()
raza_combo.grid(row=6, column=1, padx=5, pady=2, sticky='we')
raza_combo.set("")
raza_combo.bind("<<ComboboxSelected>>", lambda e: _on_raza_selected(raza_var))

correo_label = Label(frame_usuario, text='Correo:')
correo_label.grid(row=7, column=0, sticky='e', padx=5, pady=2)
correo_entry = Entry(frame_usuario)
correo_entry.grid(row=7, column=1, padx=5, pady=2)

telefono_label = Label(frame_usuario, text='Celular:')
telefono_label.grid(row=8, column=0, sticky='e', padx=5, pady=2)
telefono_entry = Entry(frame_usuario)
telefono_entry.grid(row=8, column=1, padx=5, pady=2)

extras_label = Label(frame_usuario, text='Acompañantes:')
extras_label.grid(row=9, column=0, sticky='e', padx=5, pady=2)
extras_entry = Entry(frame_usuario)
extras_entry.grid(row=9, column=1, padx=5, pady=2)

# botón registro
registro_button = Button(root_scroller.content, text='Registro', font=('Arial', 11, 'bold'), bg="#FF528B", fg='white', command=guardarDatos)
registro_button.pack(pady=15)

try:
    set_dark_theme(root)
except Exception:
    pass

_refresh_raza_options()

root.mainloop()