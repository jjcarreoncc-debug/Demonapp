import streamlit as st
import sqlite3
import pandas as pd
import os


DB_NAME = "materiales.db"


def crear_tabla():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS materiales (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            codigo_material TEXT UNIQUE,
            descripcion TEXT,
            descripcion_larga TEXT,

            categoria TEXT,
            familia TEXT,
            marca TEXT,

            tipo_material TEXT,
            estatus TEXT,

            unidad_base TEXT,

            controla_lote INTEGER,
            controla_serie INTEGER,

            peso REAL,
            volumen REAL,

            largo REAL,
            ancho REAL,
            alto REAL,

            tipo_almacenamiento TEXT,

            almacen_default TEXT,
            ubicacion_default TEXT,

            rotacion_abc TEXT,

            costo_estandar REAL,
            precio_compra REAL,
            precio_venta REAL,

            moneda TEXT,
            impuesto TEXT,

            margen_objetivo REAL,

            stock_minimo REAL,
            stock_maximo REAL,

            punto_reorden REAL,

            lead_time INTEGER,

            permite_negativo INTEGER,
            requiere_inspeccion INTEGER,

            codigo_barras TEXT,
            sku_base TEXT,
            codigo_sap TEXT,

            proveedor_principal TEXT,

            usuario_creacion TEXT
        )
    """)

    conn.commit()
    conn.close()


def insertar_materiales():

    materiales = [
        ("MAT-001", "Tornillo 1/4", "Refacción", "Ferretería", "PZA", "Activo"),
        ("MAT-002", "Caja cartón chica", "Empaque", "Cartón", "PZA", "Activo"),
        ("MAT-003", "Aceite industrial", "Materia prima", "Químicos", "LT", "Activo"),
        ("MAT-004", "Etiqueta térmica", "Empaque", "Etiquetas", "PZA", "Activo"),
        ("MAT-005", "Bolsa polietileno", "Empaque", "Plásticos", "PZA", "Activo"),
        ("MAT-006", "Motor eléctrico", "Refacción", "Eléctrico", "PZA", "Activo"),
        ("MAT-007", "Cable calibre 12", "Refacción", "Eléctrico", "MT", "Activo"),
        ("MAT-008", "Pintura blanca", "Materia prima", "Pinturas", "LT", "Activo"),
        ("MAT-009", "Tarima madera", "Empaque", "Tarimas", "PZA", "Activo"),
        ("MAT-010", "Sensor óptico", "Refacción", "Sensores", "PZA", "Activo"),
        ("MAT-011", "Cinta adhesiva", "Empaque", "Consumibles", "PZA", "Activo"),
        ("MAT-012", "Guante nitrilo", "Insumo", "Seguridad", "PZA", "Activo"),
        ("MAT-013", "Lubricante grado alimenticio", "Materia prima", "Lubricantes", "LT", "Activo"),
        ("MAT-014", "Filtro aire", "Refacción", "Filtros", "PZA", "Activo"),
        ("MAT-015", "Servicio mantenimiento", "Servicio", "Servicios", "SERV", "Activo")
    ]

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    for codigo, descripcion, categoria, familia, unidad, estatus in materiales:

        cursor.execute("""
            INSERT OR IGNORE INTO materiales (

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

                usuario_creacion

            ) VALUES (

                ?, ?, ?,
                ?, ?, ?,
                ?, ?,
                ?,
                ?, ?,
                ?, ?,
                ?, ?, ?,
                ?,
                ?, ?,
                ?,
                ?, ?, ?,
                ?, ?,
                ?,
                ?, ?,
                ?,
                ?,
                ?, ?,
                ?, ?, ?,
                ?,
                ?
            )
        """, (

            codigo,
            descripcion,
            descripcion,

            categoria,
            familia,
            "Genérico",

            "Almacenable",
            estatus,

            unidad,

            0,
            0,

            0,
            0,

            0,
            0,
            0,

            "General",

            "CEDI",
            "GEN-001",

            "B",

            10,
            12,
            18,

            "MXN",
            "IVA 16%",

            30,

            10,
            100,

            25,

            5,

            0,
            0,

            "",
            codigo,
            "",

            "Proveedor demo",

            "admin"
        ))

    conn.commit()
    conn.close()


def mostrar_datos():

    conn = sqlite3.connect(DB_NAME)

    df = pd.read_sql_query("""
        SELECT *
        FROM materiales
        ORDER BY codigo_material
    """, conn)

    conn.close()

    st.success(f"✅ Registros encontrados: {len(df)}")

    st.dataframe(
        df,
        use_container_width=True
    )


def diagnostico():

    st.subheader("🧪 Diagnóstico")

    st.write("📂 Ruta:")
    st.code(os.path.abspath(DB_NAME))

    st.write("📦 Tamaño:")
    st.write(os.path.getsize(DB_NAME))

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
    """)

    tablas = cursor.fetchall()

    conn.close()

    st.write("📋 Tablas:")
    st.write(tablas)


def app():

    st.title("🛠️ Crear materiales.db")

    if st.button("Crear tabla e insertar datos"):

        crear_tabla()

        insertar_materiales()

        st.success("✅ Base creada correctamente")

    st.markdown("---")

    diagnostico()

    st.markdown("---")

    try:
        mostrar_datos()

    except Exception as e:

        st.error("❌ Error leyendo materiales")
        st.exception(e)


if __name__ == "__main__":
    app()
