import sqlite3

from sigem_db import get_db_path


# ==========================================
# TABLA MATERIALES
# ==========================================

def crear_tablas_inventario():

    db_path = get_db_path("compras")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS materiales (

            id_material INTEGER PRIMARY KEY AUTOINCREMENT,

            codigo_material TEXT,
            descripcion TEXT,
            categoria TEXT,
            unidad_medida TEXT,

            costo REAL,
            precio REAL,

            stock_minimo REAL,
            stock_maximo REAL,

            activo INTEGER DEFAULT 1
        )
    """)

    conn.commit()
    conn.close()


# ==========================================
# TABLA MOVIMIENTOS INVENTARIO
# ==========================================

def crear_tabla_movimientos_inventario():

    db_path = get_db_path("compras")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS movimientos_inventario (

            id_movimiento INTEGER PRIMARY KEY AUTOINCREMENT,

            fecha TEXT,
            tipo_movimiento TEXT,

            codigo_material TEXT,
            descripcion TEXT,

            cantidad REAL,
            costo_unitario REAL,
            total REAL,

            bodega TEXT,
            ubicacion TEXT,

            referencia TEXT,
            comentarios TEXT,

            usuario TEXT
        )
    """)

    conn.commit()
    conn.close()
