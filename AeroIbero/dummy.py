import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(__file__), "Databases", "AeroIbero.db")

def _cols(conn, table):
    cur = conn.execute(f'PRAGMA table_info("{table}")')
    return [row[1] for row in cur.fetchall()]  # [name, ...]

def _rename_column_if_needed(conn, table, old, new):
    if old == new:
        return
    # Use double quotes to preserve/escape weird names safely
    conn.execute(f'ALTER TABLE "{table}" RENAME COLUMN "{old}" TO "{new}"')

def strip_column_whitespace(conn, table):
    names = _cols(conn, table)
    for name in names:
        trimmed = name.strip()
        if trimmed != name:
            _rename_column_if_needed(conn, table, name, trimmed)

def resolve_column(conn, table, want):
    """Find the real column by forgiving comparison (strip + lowercase)."""
    want_n = want.strip().lower()
    for c in _cols(conn, table):
        if c.strip().lower() == want_n:
            return c
    return None

def ensure_indexes(conn):
    # Rutas(Origen, Destino)
    o = resolve_column(conn, "Rutas", "Origen")
    d = resolve_column(conn, "Rutas", "Destino")
    if o and d:
        conn.execute(f'CREATE INDEX IF NOT EXISTS idx_rutas_od ON "Rutas"("{o}","{d}")')

    # Ciudades(Ciudad)
    c = resolve_column(conn, "Ciudades", "Ciudad")
    if c:
        conn.execute(f'CREATE INDEX IF NOT EXISTS idx_ciudades_nombre ON "Ciudades"("{c}")')

with sqlite3.connect(DB_PATH) as conn:
    conn.execute("PRAGMA foreign_keys = ON;")
    # 1) Normalize column names (trims whitespace) for all three tables
    for t in ("Rutas", "Resumen", "Ciudades"):
        strip_column_whitespace(conn, t)
    # 2) Create indexes using the actual resolved names
    ensure_indexes(conn)
    conn.commit()
