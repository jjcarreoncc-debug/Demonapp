import streamlit as st
import pandas as pd
import sqlite3
from sigem_db import get_db_path


def obtener_ajustes():
    try:
        db_path = get_db_path("inventarios")
        conn = sqlite3.connect(db_path)

        query = """
            SELECT
                id_ajuste,
                folio_ajuste,
                fecha,
                codigo_material,
                descripcion,
                tipo_ajuste,
                cantidad,
                stock_anterior,
                stock_nuevo,
                comentarios,
                usuario
            FROM ajustes_inventario
            ORDER BY fecha DESC, id_ajuste DESC
        """

        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    except Exception as e:
        st.error("❌ Error al consultar los ajustes de inventario.")
        st.exception(e)
        return pd.DataFrame()


def consulta_ajustes_app():
    st.title("📋 Consulta de Ajustes de Inventario")
    st.caption("Consulta histórica de ajustes aplicados al inventario físico")

    df = obtener_ajustes()

    if df.empty:
        st.warning("⚠️ No hay ajustes registrados.")
        return

    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

    st.subheader("🔎 Filtros")

    col1, col2, col3 = st.columns(3)

    with col1:
        filtro_folio = st.text_input("Folio ajuste")

    with col2:
        materiales = ["Todos"] + sorted(df["codigo_material"].dropna().unique().tolist())
        filtro_material = st.selectbox("Material", materiales)

    with col3:
        tipos = ["Todos"] + sorted(df["tipo_ajuste"].dropna().unique().tolist())
        filtro_tipo = st.selectbox("Tipo de ajuste", tipos)

    col4, col5 = st.columns(2)

    with col4:
        fecha_inicio = st.date_input(
            "Fecha inicio",
            value=df["fecha"].min().date() if df["fecha"].notna().any() else None
        )

    with col5:
        fecha_fin = st.date_input(
            "Fecha fin",
            value=df["fecha"].max().date() if df["fecha"].notna().any() else None
        )

    df_filtrado = df.copy()

    if filtro_folio:
        df_filtrado = df_filtrado[
            df_filtrado["folio_ajuste"].astype(str).str.contains(
                filtro_folio, case=False, na=False
            )
        ]

    if filtro_material != "Todos":
        df_filtrado = df_filtrado[df_filtrado["codigo_material"] == filtro_material]

    if filtro_tipo != "Todos":
        df_filtrado = df_filtrado[df_filtrado["tipo_ajuste"] == filtro_tipo]

    if fecha_inicio and fecha_fin:
        df_filtrado = df_filtrado[
            (df_filtrado["fecha"].dt.date >= fecha_inicio) &
            (df_filtrado["fecha"].dt.date <= fecha_fin)
        ]

    st.divider()

    st.subheader("📊 Resultado de consulta")

    st.metric("Total ajustes encontrados", len(df_filtrado))

    if df_filtrado.empty:
        st.warning("⚠️ No se encontraron ajustes con los filtros seleccionados.")
        return

    df_mostrar = df_filtrado.copy()
    df_mostrar["fecha"] = df_mostrar["fecha"].dt.strftime("%Y-%m-%d %H:%M:%S")

    st.dataframe(
        df_mostrar,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("📌 Resumen")

    resumen = df_filtrado.groupby("tipo_ajuste")["cantidad"].sum().reset_index()
    resumen.columns = ["Tipo de ajuste", "Cantidad total"]

    st.dataframe(
        resumen,
        use_container_width=True,
        hide_index=True
    )

    csv = df_mostrar.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        label="⬇️ Descargar consulta en CSV",
        data=csv,
        file_name="consulta_ajustes_inventario.csv",
        mime="text/csv"
    )
