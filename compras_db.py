import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "compras.db"


def get_compras_connection():

    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row

    return conn


def crear_tablas_compras():

    conn = get_compras_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS proveedores (
            id_proveedor INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            rfc TEXT,
            telefono TEXT,
            email TEXT,
            estado TEXT DEFAULT 'Activo'
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS entradas_compras (
            id_entrada INTEGER PRIMARY KEY AUTOINCREMENT,
            id_proveedor INTEGER,
            proveedor TEXT,
            factura TEXT NOT NULL,
            fecha_factura TEXT,
            fecha_recepcion TEXT,
            moneda TEXT DEFAULT 'MXN',
            tipo_cambio REAL DEFAULT 1,
            subtotal REAL DEFAULT 0,
            impuesto_total REAL DEFAULT 0,
            total REAL DEFAULT 0,
            archivo_adjunto TEXT,
            comentarios TEXT,
            estado TEXT DEFAULT 'BORRADOR',
            fecha_creacion TEXT,
            usuario_creacion TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS entradas_compras_detalle (
            id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
            id_entrada INTEGER NOT NULL,
            codigo_material TEXT NOT NULL,
            descripcion TEXT,
            cantidad REAL NOT NULL,
            costo_unitario REAL DEFAULT 0,
            impuesto REAL DEFAULT 0,
            total REAL DEFAULT 0,
            bodega TEXT,
            ubicacion TEXT
        )
    """)

    conn.commit()
    conn.close()
