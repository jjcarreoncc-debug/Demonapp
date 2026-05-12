import sqlite3

from sigem_db import get_db_path


def crear_tablas_inventario():

    db_path = get_db_path("materiales")

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


def crear_tabla_movimientos_inventario():

    db_path = get_db_path("inventarios")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS movimientos_inventario (
            id_movimiento INTEGER PRIMARY KEY AUTOINCREMENT,
            folio_movimiento TEXT,
            fecha TEXT,
            tipo_movimiento TEXT,
            tipo_documento TEXT,
            numero_documento TEXT,
            archivo_documento TEXT,
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

    columnas_nuevas = [
        ("folio_movimiento", "TEXT"),
        ("tipo_documento", "TEXT"),
        ("numero_documento", "TEXT"),
        ("archivo_documento", "TEXT"),
        ("referencia", "TEXT"),
        ("comentarios", "TEXT"),
        ("usuario", "TEXT"),
    ]

    for nombre_columna, tipo_columna in columnas_nuevas:
        try:
            cur.execute(
                f"ALTER TABLE movimientos_inventario ADD COLUMN {nombre_columna} {tipo_columna}"
            )
        except sqlite3.OperationalError:
            pass

    conn.commit()
    conn.close()


def crear_tabla_inventario_fisico():

    db_path = get_db_path("inventarios")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS inventario_fisico (
            id_conteo INTEGER PRIMARY KEY AUTOINCREMENT,

            folio_conteo TEXT,
            fecha_conteo TEXT,

            codigo_material TEXT,
            descripcion TEXT,

            bodega TEXT,
            ubicacion TEXT,

            cantidad_sistema REAL DEFAULT 0,
            cantidad_fisica REAL DEFAULT 0,
            diferencia REAL DEFAULT 0,

            usuario TEXT,
            estatus TEXT DEFAULT 'Pendiente'
        )
    """)

    columnas_nuevas = [
        ("folio_conteo", "TEXT"),
        ("fecha_conteo", "TEXT"),
        ("codigo_material", "TEXT"),
        ("descripcion", "TEXT"),
        ("bodega", "TEXT"),
        ("ubicacion", "TEXT"),
        ("cantidad_sistema", "REAL DEFAULT 0"),
        ("cantidad_fisica", "REAL DEFAULT 0"),
        ("diferencia", "REAL DEFAULT 0"),
        ("usuario", "TEXT"),
        ("estatus", "TEXT DEFAULT 'Pendiente'"),
    ]

    for nombre_columna, tipo_columna in columnas_nuevas:
        try:
            cur.execute(
                f"ALTER TABLE inventario_fisico ADD COLUMN {nombre_columna} {tipo_columna}"
            )
        except sqlite3.OperationalError:
            pass

    conn.commit()
    conn.close()
