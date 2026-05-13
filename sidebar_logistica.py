import streamlit as st


def sidebar_logistica():

    menu_logistica = None
    submenu_logistica = None
    opcion_logistica = None


    st.sidebar.markdown("## 🚚 Logística")


    # ==========================================
    # INICIO
    # ==========================================

    if st.sidebar.button(
        "🏠 Inicio",
        use_container_width=True
    ):
        menu_logistica = "Inicio"


    # ==========================================
    # EMBARQUES
    # ==========================================

    st.sidebar.markdown("### 📦 Embarques")

    if st.sidebar.button(
        "➕ Generar embarque",
        use_container_width=True
    ):
        menu_logistica = "Embarques"
        submenu_logistica = "Generar"
        opcion_logistica = "➕ Generar embarque"


    if st.sidebar.button(
        "📦 Carga embarque",
        use_container_width=True
    ):
        menu_logistica = "Embarques"
        submenu_logistica = "Carga"
        opcion_logistica = "📦 Carga embarque"


    if st.sidebar.button(
        "📋 Consultar embarques",
        use_container_width=True
    ):
        menu_logistica = "Embarques"
        submenu_logistica = "Consulta"
        opcion_logistica = "📋 Consultar embarques"


    # ==========================================
    # TRANSPORTE
    # ==========================================

    st.sidebar.markdown("### 🚛 Transporte")

    if st.sidebar.button(
        "🚚 Transportistas",
        use_container_width=True
    ):
        menu_logistica = "Transporte"
        opcion_logistica = "🚚 Transportistas"


    if st.sidebar.button(
        "🚗 Vehículos",
        use_container_width=True
    ):
        menu_logistica = "Transporte"
        opcion_logistica = "🚗 Vehículos"


    # ==========================================
    # TRACKING
    # ==========================================

    st.sidebar.markdown("### 📡 Tracking")

    if st.sidebar.button(
        "📍 Seguimiento embarque",
        use_container_width=True
    ):
        menu_logistica = "Tracking"
        opcion_logistica = "📍 Seguimiento embarque"


    return (
        menu_logistica,
        submenu_logistica,
        opcion_logistica
    )
