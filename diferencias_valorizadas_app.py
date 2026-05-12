import sqlite3
from io import BytesIO

import pandas as pd
import streamlit as st

from sigem_db import get_db_path


def obtener_diferencias_valorizadas():

    conn = sqlite3.connect(get_db_path("inventarios"))

    materiales_path = get_db_path("materiales")

    conn.execute(f"""
        ATTACH DATABASE '{materiales_path}' AS materiales_db
    """)

    query = """
        SELECT
            f.folio_conteo,
            f.fecha_conteo,
            f.codigo_material,
            f.descripcion AS descripcion_corta,

            m.descripcion_larga,
            m.categoria,
            m.familia,
            m.marca,
            m.tipo_material,

            f.bodega,
            f.ubicacion,
            m.tipo_almacenamiento,

            f.cantidad_sistema,
            f.cantidad_fisica,
            f.diferencia,

            m.unidad_base,

            COALESCE(m.costo_estandar, 0) AS costo_estandar,
            COALESCE(m.precio_compra, 0) AS precio_compra,
            COALESCE(m.precio_venta, 0) AS precio_venta,

            (f.diferencia * COALESCE(m.costo_estandar, 0)) AS impacto_valorizado,
            ABS(f.diferencia * COALESCE(m.costo_estandar, 0)) AS valor_absoluto_impacto,

            m.stock_minimo,
            m.stock_maximo,
            m.rotacion_abc,

            CASE
                WHEN f.diferencia > 0 THEN 'SOBRANTE'
                WHEN f.diferencia < 0 THEN 'FALTANTE'
                ELSE 'SIN DIFERENCIA'
            END AS tipo_diferencia,

            f.usuario AS usuario_conteo,
            f.estatus,
            f.observaciones AS comentarios

        FROM inventario_fisico f

        LEFT JOIN materiales_db.materiales m
            ON f.codigo_material = m.codigo_material

        WHERE f.diferencia <> 0

        ORDER BY valor_absoluto_impacto DESC
    """

    try:
        df = pd.read_sql_query(query, conn)

    except Exception as e:
        conn.close()
        st.error("❌ Error consultando diferencias valorizadas.")
        st.exception(e)
        return pd.DataFrame()

    conn.close()
    return df


def convertir_excel(df):

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(
            writer,
            index=False,
            sheet_name="Diferencias valorizadas"
        )

    return output.getvalue()


def diferencias_valorizadas_app():

    st.title("💰 Diferencias valorizadas")
    st.caption("Reporte valorizado de diferencias de inventario físico")

    df = obtener_diferencias_valorizadas()

    if df.empty:
        st.info("No hay diferencias valorizadas para mostrar.")
        return

    st.subheader("🔎 Filtros")

    col1, col2, col3 = st.columns(3)

    with col1:
        folio = st.text_input("Folio conteo")

    with col2:
        tipo = st.selectbox(
            "Tipo diferencia",
            ["Todos"] + sorted(df["tipo_diferencia"].dropna().unique().tolist())
        )

    with col3:
        estatus = st.selectbox(
            "Estatus",
            ["Todos"] + sorted(df["estatus"].dropna().unique().tolist())
        )

    col4, col5, col6 = st.columns(3)

    with col4:
        categoria = st.selectbox(
            "Categoría",
            ["Todos"] + sorted(df["categoria"].dropna().unique().tolist())
        )

    with col5:
        familia = st.selectbox(
            "Familia",
            ["Todos"] + sorted(df["familia"].dropna().unique().tolist())
        )

    with col6:
        bodega = st.selectbox(
            "Bodega",
            ["Todos"] + sorted(df["bodega"].dropna().unique().tolist())
        )

    df_filtrado = df.copy()

    if folio:
        df_filtrado = df_filtrado[
            df_filtrado["folio_conteo"].astype(str).str.contains(
                folio,
                case=False,
                na=False
            )
        ]

    if tipo != "Todos":
        df_filtrado = df_filtrado[df_filtrado["tipo_diferencia"] == tipo]

    if estatus != "Todos":
        df_filtrado = df_filtrado[df_filtrado["estatus"] == estatus]

    if categoria != "Todos":
        df_filtrado = df_filtrado[df_filtrado["categoria"] == categoria]

    if familia != "Todos":
        df_filtrado = df_filtrado[df_filtrado["familia"] == familia]

    if bodega != "Todos":
        df_filtrado = df_filtrado[df_filtrado["bodega"] == bodega]

    st.divider()

    total_sobrantes = df_filtrado.loc[
        df_filtrado["impacto_valorizado"] > 0,
        "impacto_valorizado"
    ].sum()

    total_faltantes = df_filtrado.loc[
        df_filtrado["impacto_valorizado"] < 0,
        "impacto_valorizado"
    ].sum()

    impacto_total = df_filtrado["impacto_valorizado"].sum()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Registros", len(df_filtrado))
    c2.metric("Sobrantes $", round(total_sobrantes, 2))
    c3.metric("Faltantes $", round(total_faltantes, 2))
    c4.metric("Impacto neto $", round(impacto_total, 2))

    st.subheader("📊 Reporte")

    st.dataframe(
        df_filtrado,
        use_container_width=True,
        hide_index=True
    )

    excel = convertir_excel(df_filtrado)

    st.download_button(
        label="⬇️ Descargar Excel",
        data=excel,
        file_name="diferencias_valorizadas.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
