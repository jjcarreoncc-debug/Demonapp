import streamlit as st
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "materiales.db"


st.title("🛠️ Crear tabla materiales")

st.write("📂 Base donde se va a crear:")
st.code(str(DB_PATH))

st.write("Existe DB:")
st.write(DB_PATH.exists())

st.write("Tamaño actual:")
st.write(DB_PATH.stat().st_size if DB_PATH.exists() else 0)


if st.button("🚀 Crear tabla materiales"):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
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

    tablas = cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        ORDER BY name
    """).fetchall()

    conn.close()

    st.success("✅ Proceso terminado")
    st.write("📋 Tablas encontradas:")
    st.write(tablas)

    st.write("📏 Nuevo tamaño:")
    st.write(DB_PATH.stat().st_size)
