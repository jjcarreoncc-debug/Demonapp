import streamlit as st
import pandas as pd
import sqlite3
import os


DB_NAME = "materiales.db"


def crear_tabla_y_datos():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS materiales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_material TEXT UNIQUE,
            descripcion TEXT,
            categoria TEXT,
            familia TEXT,
            unidad_base TEXT,
            estatus TEXT
        )
    """)

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
        ("MAT-015", "Servicio mantenimiento", "Servicio", "Servicios", "SERV", "Activo"),
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO materiales (
            codigo_material,
            descripcion,
            categoria,
            familia,
            unidad_base,
            estatus
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, materiales)

    conn.commit()
    conn.close()


def tabla_existe():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name='materiales'
    """)

    existe = cursor.fetchone() is not None
    conn.close()

    return existe


def consulta_material_app():
    st.title("🔍 Consulta de materiales")

    st.caption(f"Base usada: {os.path.abspath(DB_NAME)}")

    if not tabla_existe():
        st.warning("La tabla materiales no existía. Se va a crear automáticamente.")
        crear_tabla_y_datos()
        st.success("✅ Tabla creada y datos insertados")

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
        use_container_width=True,
        hide_index=True
    )


if __name__ == "__main__":
    consulta_material_app()
