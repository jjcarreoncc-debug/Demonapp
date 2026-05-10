import streamlit as st
import pandas as pd
import sqlite3
import os


DB_NAME = "materiales.db"


def obtener_materiales():

    conn = sqlite3.connect(DB_NAME)

    query = """
        SELECT *
        FROM materiales
        ORDER BY codigo_material
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


def consulta_material_app():

    st.title("🔍 Consulta de materiales")

    st.caption(
        "Maestros / Productos / Maestro de materiales / Consulta"
    )

    st.write(f"📂 Base usada: {os.path.abspath(DB_NAME)}")

    # =====================================================
    # CARGAR DATOS
    # =====================================================

    try:

        df = obtener_materiales()

    except Exception as e:

        st.error("❌ Error consultando materiales")
        st.exception(e)
        return

    # =====================================================
    # VALIDAR DATOS
    # =====================================================

    if df.empty:
        st.warning("No hay materiales registrados")
        return

    st.success(f"✅ Registros encontrados: {len(df)}")

    # =====================================================
    # RENOMBRAR COLUMNAS
    # =====================================================

    df = df.rename(columns={

        "codigo_material": "Código",
        "descripcion": "Descripción",
        "categoria": "Categoría",
        "familia": "Familia",
        "unidad_base": "Unidad",
        "estatus": "Estatus",

    })

    # =====================================================
    # FILTROS
    # =====================================================

    st.markdown("---")
    st.subheader("🎯 Filtros de búsqueda")

    c1, c2, c3 = st.columns(3)

    with c1:

        filtro_codigo = st.text_input(
            "Código material"
        )

        categorias = (
            ["Todas"] +
            sorted(
                df["Categoría"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )
        )

        filtro_categoria = st.selectbox(
            "Categoría",
            categorias
        )

    with c2:

        filtro_descripcion = st.text_input(
            "Descripción"
        )

        filtro_familia = st.text_input(
            "Familia"
        )

    with c3:

        estatus = (
            ["Todos"] +
            sorted(
                df["Estatus"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )
        )

        filtro_estatus = st.selectbox(
            "Estatus",
            estatus
        )

        unidades = (
            ["Todas"] +
            sorted(
                df["Unidad"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )
        )

        filtro_unidad = st.selectbox(
            "Unidad",
            unidades
        )

    # =====================================================
    # FILTRAR
    # =====================================================

    df_filtrado = df.copy()

    if filtro_codigo:

        df_filtrado = df_filtrado[
            df_filtrado["Código"]
            .astype(str)
            .str.contains(
                filtro_codigo,
                case=False,
                na=False
            )
        ]

    if filtro_descripcion:

        df_filtrado = df_filtrado[
            df_filtrado["Descripción"]
            .astype(str)
            .str.contains(
                filtro_descripcion,
                case=False,
                na=False
            )
        ]

    if filtro_categoria != "Todas":

        df_filtrado = df_filtrado[
            df_filtrado["Categoría"] == filtro_categoria
        ]

    if filtro_familia:

        df_filtrado = df_filtrado[
            df_filtrado["Familia"]
            .astype(str)
            .str.contains(
                filtro_familia,
                case=False,
                na=False
            )
        ]

    if filtro_estatus != "Todos":

        df_filtrado = df_filtrado[
            df_filtrado["Estatus"] == filtro_estatus
        ]

    if filtro_unidad != "Todas":

        df_filtrado = df_filtrado[
            df_filtrado["Unidad"] == filtro_unidad
        ]

    # =====================================================
    # RESULTADOS
    # =====================================================

    st.markdown("---")
    st.subheader("📋 Resultados")

    if df_filtrado.empty:

        st.warning(
            "No se encontraron materiales con esos filtros"
        )

        return

    columnas = [

        "Código",
        "Descripción",
        "Categoría",
        "Familia",
        "Unidad",
        "Estatus"

    ]

    st.dataframe(

        df_filtrado[columnas],

        use_container_width=True,
        hide_index=True

    )

    # =====================================================
    # DETALLE
    # =====================================================

    st.markdown("---")
    st.subheader("📄 Detalle del material")

    material = st.selectbox(

        "Selecciona material",

        df_filtrado["Código"]
        .astype(str)
        .tolist()

    )

    fila = df_filtrado[
        df_filtrado["Código"]
        .astype(str) == material
    ].iloc[0]

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "Código",
            fila.get("Código", "")
        )

        st.metric(
            "Categoría",
            fila.get("Categoría", "")
        )

    with c2:

        st.metric(
            "Unidad",
            fila.get("Unidad", "")
        )

        st.metric(
            "Estatus",
            fila.get("Estatus", "")
        )

    with c3:

        st.metric(
            "Familia",
            fila.get("Familia", "")
        )

    st.info(
        f"Descripción: {fila.get('Descripción', '')}"
    )

    # =====================================================
    # BOTONES
    # =====================================================

    st.markdown("---")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.button("✏️ Modificar")

    with c2:
        st.button("❌ Baja")

    with c3:
        st.button("📥 Exportar")


if __name__ == "__main__":
    consulta_material_app()
