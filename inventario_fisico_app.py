import sqlite3
from datetime import datetime

import pandas as pd
import streamlit as st

from sigem_db import get_db_path


def obtener_materiales():
    conn = sqlite3.connect(get_db_path("materiales"))

    try:
        df = pd.read_sql_query("""
            SELECT 
                codigo_material,
                descripcion
            FROM materiales
            WHERE estatus = 'Activo'
            ORDER BY codigo_material
        """, conn)
    except Exception:
        df = pd.DataFrame(columns=["codigo_material", "descripcion"])

    conn.close()
    return df


def obtener_existencia(codigo_material):
    conn = sqlite3.connect(get_db_path("inventarios"))
    cur = conn.cursor()

    cur.execute("""
        SELECT COALESCE(SUM(cantidad), 0)
        FROM movimientos_inventario
        WHERE codigo_material = ?
    """, (codigo_material,))

    existencia = cur.fetchone()[0]

    conn.close()
    return float(existencia or 0)


def guardar_conteo(
    folio_conteo,
    fecha_conteo,
    codigo_material,
    descripcion,
    bodega,
    ubicacion,
    cantidad_sistema,
    cantidad_fisica,
    diferencia,
    usuario
):
    conn = sqlite3.connect(get_db_path("inventarios"))
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO inventario_fisico (
            folio_conteo,
            fecha_conteo,
            codigo_material,
            descripcion,
            bodega,
            ubicacion,
            cantidad_sistema,
            cantidad_fisica,
            diferencia,
            usuario,
            estatus
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        folio_conteo,
        fecha_conteo,
        codigo_material,
        descripcion,
        bodega,
        ubicacion,
        cantidad_sistema,
        cantidad_fisica,
        diferencia,
        usuario,
        "Pendiente"
    ))

    conn.commit()
    conn.close()


def consultar_conteos():
    conn = sqlite3.connect(get_db_path("inventarios"))

    try:
        df = pd.read_sql_query("""
            SELECT
                id_conteo,
                folio_conteo,
                fecha_conteo,
                codigo_material,
                descripcion,
                bodega,
                ubicacion,
                cantidad_sistema,
                cantidad_fisica,
                diferencia,
                usuario,
                estatus
            FROM inventario_fisico
            ORDER BY id_conteo DESC
        """, conn)
    except Exception:
        df = pd.DataFrame()

    conn.close()
    return df


def inventario_fisico_app():

    st.title("📋 Inventario físico")
    st.caption("Conteo físico de inventario vs existencia del sistema")

    tab1, tab2 = st.tabs([
        "➕ Capturar conteo",
        "📊 Consultar conteos"
    ])

    with tab1:

        st.subheader("➕ Captura de conteo físico")

        materiales = obtener_materiales()

        if materiales.empty:
            st.warning("No hay materiales con estatus Activo registrados en materiales.db.")
            st.stop()

        hora_actual = datetime.now().strftime("%H%M%S")
        folio_default = f"IF-{datetime.now().strftime('%Y%m%d')}-{hora_actual}"

        col1, col2 = st.columns(2)

        with col1:
            folio_conteo = st.text_input("Folio conteo", value=folio_default)
            fecha_conteo = st.date_input("Fecha conteo")

        with col2:
            bodega = st.text_input("Bodega / Almacén", value="Principal")
            ubicacion = st.text_input("Ubicación", value="General")

        lista_materiales = materiales.apply(
            lambda row: f"{row['codigo_material']} - {row['descripcion']}",
            axis=1
        ).tolist()

        material_sel = st.selectbox("Material", lista_materiales)

        codigo_material = material_sel.split(" - ")[0]

        descripcion = materiales.loc[
            materiales["codigo_material"] == codigo_material,
            "descripcion"
        ].iloc[0]

        cantidad_sistema = obtener_existencia(codigo_material)

        st.info(f"Existencia sistema: {cantidad_sistema}")

        cantidad_fisica = st.number_input(
            "Cantidad física contada",
            min_value=0.0,
            step=1.0
        )

        diferencia = cantidad_fisica - cantidad_sistema

        col3, col4, col5 = st.columns(3)

        with col3:
            st.metric("Sistema", cantidad_sistema)

        with col4:
            st.metric("Físico", cantidad_fisica)

        with col5:
            st.metric("Diferencia", diferencia)

        usuario = st.text_input("Usuario", value="admin")

        if st.button("💾 Guardar conteo físico", use_container_width=True):

            guardar_conteo(
                folio_conteo=folio_conteo,
                fecha_conteo=str(fecha_conteo),
                codigo_material=codigo_material,
                descripcion=descripcion,
                bodega=bodega,
                ubicacion=ubicacion,
                cantidad_sistema=cantidad_sistema,
                cantidad_fisica=cantidad_fisica,
                diferencia=diferencia,
                usuario=usuario
            )

            st.success("Conteo físico guardado correctamente.")

    with tab2:

        st.subheader("📊 Conteos físicos registrados")

        df_conteos = consultar_conteos()

        if df_conteos.empty:
            st.info("Todavía no hay conteos físicos registrados.")
        else:
            st.dataframe(df_conteos, use_container_width=True)
