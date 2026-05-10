from datetime import datetime
from database import get_connection


def crear_tabla_materiales():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS materiales (
            id_material INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_material TEXT UNIQUE NOT NULL,
            descripcion TEXT NOT NULL,
            descripcion_larga TEXT,
            categoria TEXT,
            familia TEXT,
            marca TEXT,
            tipo_material TEXT,
            estatus TEXT DEFAULT 'Activo',
            unidad_base TEXT,
            controla_lote INTEGER DEFAULT 0,
            controla_serie INTEGER DEFAULT 0,
            peso REAL DEFAULT 0,
            volumen REAL DEFAULT 0,
            largo REAL DEFAULT 0,
            ancho REAL DEFAULT 0,
            alto REAL DEFAULT 0,
            tipo_almacenamiento TEXT,
            almacen_default TEXT,
            ubicacion_default TEXT,
            rotacion_abc TEXT,
            costo_estandar REAL DEFAULT 0,
            precio_compra REAL DEFAULT 0,
            precio_venta REAL DEFAULT 0,
            moneda TEXT,
            impuesto TEXT,
            margen_objetivo REAL DEFAULT 0,
            stock_minimo REAL DEFAULT 0,
            stock_maximo REAL DEFAULT 0,
            punto_reorden REAL DEFAULT 0,
            lead_time INTEGER DEFAULT 0,
            permite_negativo INTEGER DEFAULT 0,
            requiere_inspeccion INTEGER DEFAULT 0,
            codigo_barras TEXT,
            sku_base TEXT,
            codigo_sap TEXT,
            proveedor_principal TEXT,
            fecha_creacion TEXT,
            usuario_creacion TEXT,
            fecha_baja TEXT,
            motivo_baja TEXT,
            comentarios_baja TEXT
        )
    """)

    conn.commit()
    conn.close()


def insertar_material(data):

    crear_tabla_materiales()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO materiales (
            codigo_material,
            descripcion,
            descripcion_larga,
            categoria,
            familia,
            marca,
            tipo_material,
            estatus,
            unidad_base,
            controla_lote,
            controla_serie,
            peso,
            volumen,
            largo,
            ancho,
            alto,
            tipo_almacenamiento,
            almacen_default,
            ubicacion_default,
            rotacion_abc,
            costo_estandar,
            precio_compra,
            precio_venta,
            moneda,
            impuesto,
            margen_objetivo,
            stock_minimo,
            stock_maximo,
            punto_reorden,
            lead_time,
            permite_negativo,
            requiere_inspeccion,
            codigo_barras,
            sku_base,
            codigo_sap,
            proveedor_principal,
            fecha_creacion,
            usuario_creacion
        )
        VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?
        )
    """, (
        data["codigo_material"],
        data["descripcion"],
        data["descripcion_larga"],
        data["categoria"],
        data["familia"],
        data["marca"],
        data["tipo_material"],
        data["estatus"],
        data["unidad_base"],
        int(data["controla_lote"]),
        int(data["controla_serie"]),
        data["peso"],
        data["volumen"],
        data["largo"],
        data["ancho"],
        data["alto"],
        data["tipo_almacenamiento"],
        data["almacen_default"],
        data["ubicacion_default"],
        data["rotacion_abc"],
        data["costo_estandar"],
        data["precio_compra"],
        data["precio_venta"],
        data["moneda"],
        data["impuesto"],
        data["margen_objetivo"],
        data["stock_minimo"],
        data["stock_maximo"],
        data["punto_reorden"],
        data["lead_time"],
        int(data["permite_negativo"]),
        int(data["requiere_inspeccion"]),
        data["codigo_barras"],
        data["sku_base"],
        data["codigo_sap"],
        data["proveedor_principal"],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        data.get("usuario_creacion", "admin")
    ))

    conn.commit()
    conn.close()

def consultar_materiales():
    import sqlite3

    conn = sqlite3.connect("materiales.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM materiales
        ORDER BY codigo_material
    """)

    registros = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return registros





