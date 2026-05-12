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

    st.caption(
        "Proceso de creación y captura de conteos físicos"
    )

    tab1, tab2, tab3 = st.tabs([
        "➕ Crear conteo",
        "✍️ Capturar conteo",
        "📊 Consultar conteos"
    ])

    # ==================================================
    # CREAR CONTEO
    # ==================================================
    with tab1:

        st.subheader("➕ Crear conteo físico")

        materiales = obtener_materiales()

        if materiales.empty:
            st.warning(
                "No hay materiales activos registrados."
            )
            st.stop()

        hora_actual = datetime.now().strftime("%H%M%S")

        folio_default = (
            f"IF-{datetime.now().strftime('%Y%m%d')}-{hora_actual}"
        )

        col1, col2 = st.columns(2)

        with col1:

            folio_conteo = st.text_input(
                "Folio conteo",
                value=folio_default,
                key="crear_folio"
            )

            fecha_conteo = st.date_input(
                "Fecha conteo",
                key="crear_fecha"
            )

        with col2:

            bodega = st.text_input(
                "Bodega / Almacén",
                value="Principal",
                key="crear_bodega"
            )

            ubicacion = st.text_input(
                "Ubicación",
                value="General",
                key="crear_ubicacion"
            )

        lista_materiales = materiales.apply(
            lambda row:
            f"{row['codigo_material']} - {row['descripcion']}",
            axis=1
        ).tolist()

        material_sel = st.selectbox(
            "Material",
            lista_materiales,
            key="crear_material"
        )

        codigo_material = material_sel.split(" - ")[0]

        descripcion = materiales.loc[
            materiales["codigo_material"] == codigo_material,
            "descripcion"
        ].iloc[0]

        cantidad_sistema = obtener_existencia(
            codigo_material
        )

        st.info(
            f"Existencia sistema actual: {cantidad_sistema}"
        )

        usuario = st.text_input(
            "Usuario",
            value="admin",
            key="crear_usuario"
        )

        st.warning(
            "En Crear conteo NO se captura cantidad física."
        )

        if st.button(
            "💾 Crear conteo",
            use_container_width=True,
            key="btn_crear_conteo"
        ):

            guardar_conteo(
                folio_conteo=folio_conteo,
                fecha_conteo=str(fecha_conteo),
                codigo_material=codigo_material,
                descripcion=descripcion,
                bodega=bodega,
                ubicacion=ubicacion,
                cantidad_sistema=cantidad_sistema,
                cantidad_fisica=0,
                diferencia=0,
                usuario=usuario
            )

            st.success(
                "Conteo creado correctamente."
            )

    # ==================================================
    # CAPTURAR CONTEO
    # ==================================================
    with tab2:

        st.subheader("✍️ Capturar conteo físico")

        st.info(
            "Aquí se capturan las cantidades físicas contadas."
        )

        df_conteos = consultar_conteos()

        if df_conteos.empty:

            st.warning(
                "No existen conteos creados."
            )

        else:

            st.dataframe(
                df_conteos,
                use_container_width=True
            )

    # ==================================================
    # CONSULTAR CONTEOS
    # ==================================================
    with tab3:

        st.subheader("📊 Conteos físicos registrados")

        df_conteos = consultar_conteos()

        if df_conteos.empty:

            st.info(
                "Todavía no hay conteos físicos registrados."
            )

        else:

            st.dataframe(
                df_conteos,
                use_container_width=True
            )
