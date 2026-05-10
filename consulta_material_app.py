import streamlit as st
import pandas as pd


def consulta_material_app():

    st.title("🔍 Consulta de material")

    st.caption(
        "Maestros / Productos / Maestro de materiales / Consulta de material"
    )

    # =========================
    # FILTROS
    # =========================
    st.subheader("🎯 Filtros de búsqueda")

    c1, c2, c3 = st.columns(3)

    with c1:
        codigo_material = st.text_input("Código material")
        categoria = st.selectbox(
            "Categoría",
            [
                "Todas",
                "Materia prima",
                "Producto terminado",
                "Empaque",
                "Refacción",
                "Servicio"
            ]
        )

    with c2:
        descripcion = st.text_input("Descripción")
        familia = st.text_input("Familia")

    with c3:
        estatus = st.selectbox(
            "Estatus",
            [
                "Todos",
                "Activo",
                "Bloqueado",
                "Descontinuado"
            ]
        )
        unidad_base = st.selectbox(
            "Unidad base",
            [
                "Todas",
                "PZA",
                "KG",
                "LT",
                "CJ",
                "MT"
            ]
        )

    buscar = st.button("🔎 Buscar material")

    st.markdown("---")

    # =========================
    # DATA DEMO TEMPORAL
    # =========================
    data = [
        {
            "Código": "MAT-001",
            "Descripción": "Tornillo 1/4",
            "Categoría": "Refacción",
            "Familia": "Ferretería",
            "Unidad": "PZA",
            "Estatus": "Activo",
            "Stock mínimo": 50,
            "Stock máximo": 500,
            "ABC": "B"
        },
        {
            "Código": "MAT-002",
            "Descripción": "Caja cartón chica",
            "Categoría": "Empaque",
            "Familia": "Cartón",
            "Unidad": "PZA",
            "Estatus": "Activo",
            "Stock mínimo": 100,
            "Stock máximo": 1000,
            "ABC": "A"
        },
        {
            "Código": "MAT-003",
            "Descripción": "Aceite industrial",
            "Categoría": "Materia prima",
            "Familia": "Químicos",
            "Unidad": "LT",
            "Estatus": "Bloqueado",
            "Stock mínimo": 20,
            "Stock máximo": 200,
            "ABC": "C"
        }
    ]

    df = pd.DataFrame(data)

    # =========================
    # FILTRADO DEMO
    # =========================
    if codigo_material:
        df = df[df["Código"].str.contains(codigo_material, case=False, na=False)]

    if descripcion:
        df = df[df["Descripción"].str.contains(descripcion, case=False, na=False)]

    if categoria != "Todas":
        df = df[df["Categoría"] == categoria]

    if familia:
        df = df[df["Familia"].str.contains(familia, case=False, na=False)]

    if estatus != "Todos":
        df = df[df["Estatus"] == estatus]

    if unidad_base != "Todas":
        df = df[df["Unidad"] == unidad_base]

    # =========================
    # RESULTADOS
    # =========================
    st.subheader("📋 Resultados")

    if df.empty:
        st.warning("No se encontraron materiales con esos filtros.")
        return

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    # =========================
    # DETALLE MATERIAL
    # =========================
    st.subheader("📄 Detalle del material")

    material = st.selectbox(
        "Selecciona material",
        df["Código"].tolist()
    )

    fila = df[df["Código"] == material].iloc[0]

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Código", fila["Código"])
        st.metric("Categoría", fila["Categoría"])

    with c2:
        st.metric("Unidad", fila["Unidad"])
        st.metric("Estatus", fila["Estatus"])

    with c3:
        st.metric("ABC", fila["ABC"])
        st.metric("Stock máx.", fila["Stock máximo"])

    st.info(f"Descripción: {fila['Descripción']}")

    st.markdown("---")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.button("✏️ Modificar material")

    with c2:
        st.button("❌ Solicitar baja")

    with c3:
        st.button("📥 Exportar consulta")
