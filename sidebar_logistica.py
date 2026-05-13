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
        submenu_logistica = "Inicio"
        opcion_logistica = "🏠 Inicio"


    # ==========================================
    # EMBARQUES
    # ==========================================

    st.sidebar.markdown("### 📦 Embarques")


    if st.sidebar.button(
        "➕ Alta embarque",
        use_container_width=True
    ):
        menu_logistica = "📦 Embarques"
        submenu_logistica = "Embarques"
        opcion_logistica = "➕ Alta embarque"


    if st.sidebar.button(
        "❌ Baja embarque",
        use_container_width=True
    ):
        menu_logistica = "📦 Embarques"
        submenu_logistica = "Embarques"
        opcion_logistica = "❌ Baja embarque"


    if st.sidebar.button(
        "📋 Consulta embarque",
        use_container_width=True
    ):
        menu_logistica = "📦 Embarques"
        submenu_logistica = "Embarques"
        opcion_logistica = "📋 Consulta embarque"


    if st.sidebar.button(
        "✏️ Editar embarque",
        use_container_width=True
    ):
        menu_logistica = "📦 Embarques"
        submenu_logistica = "Embarques"
        opcion_logistica = "✏️ Editar embarque"


    # ==========================================
    # TRANSPORTE
    # ==========================================

    st.sidebar.markdown("### 🚛 Transporte")


    # ==========================================
    # TRANSPORTISTAS
    # ==========================================

    st.sidebar.markdown("#### 👥 Transportistas")


    if st.sidebar.button(
        "➕ Alta transportista",
        use_container_width=True
    ):
        menu_logistica = "🚛 Transporte"
        submenu_logistica = "👥 Transportistas"
        opcion_logistica = "➕ Alta transportista"


    if st.sidebar.button(
        "❌ Baja transportista",
        use_container_width=True
    ):
        menu_logistica = "🚛 Transporte"
        submenu_logistica = "👥 Transportistas"
        opcion_logistica = "❌ Baja transportista"


    if st.sidebar.button(
        "📋 Consulta transportista",
        use_container_width=True
    ):
        menu_logistica = "🚛 Transporte"
        submenu_logistica = "👥 Transportistas"
        opcion_logistica = "📋 Consulta transportista"


    if st.sidebar.button(
        "✏️ Editar transportista",
        use_container_width=True
    ):
        menu_logistica = "🚛 Transporte"
        submenu_logistica = "👥 Transportistas"
        opcion_logistica = "✏️ Editar transportista"


    # ==========================================
    # VEHICULOS
    # ==========================================

    st.sidebar.markdown("#### 🚚 Vehículos")


    if st.sidebar.button(
        "➕ Alta vehículo",
        use_container_width=True
    ):
        menu_logistica = "🚛 Transporte"
        submenu_logistica = "🚚 Vehículos"
        opcion_logistica = "➕ Alta vehículo"


    if st.sidebar.button(
        "❌ Baja vehículo",
        use_container_width=True
    ):
        menu_logistica = "🚛 Transporte"
        submenu_logistica = "🚚 Vehículos"
        opcion_logistica = "❌ Baja vehículo"


    if st.sidebar.button(
        "📋 Consulta vehículo",
        use_container_width=True
    ):
        menu_logistica = "🚛 Transporte"
        submenu_logistica = "🚚 Vehículos"
        opcion_logistica = "📋 Consulta vehículo"


    if st.sidebar.button(
        "✏️ Editar vehículo",
        use_container_width=True
    ):
        menu_logistica = "🚛 Transporte"
        submenu_logistica = "🚚 Vehículos"
        opcion_logistica = "✏️ Editar vehículo"


    # ==========================================
    # OPERADORES
    # ==========================================

    st.sidebar.markdown("#### 👨 Operadores")


    if st.sidebar.button(
        "➕ Alta operador",
        use_container_width=True
    ):
        menu_logistica = "🚛 Transporte"
        submenu_logistica = "👨 Operadores"
        opcion_logistica = "➕ Alta operador"


    if st.sidebar.button(
        "❌ Baja operador",
        use_container_width=True
    ):
        menu_logistica = "🚛 Transporte"
        submenu_logistica = "👨 Operadores"
        opcion_logistica = "❌ Baja operador"


    if st.sidebar.button(
        "📋 Consulta operador",
        use_container_width=True
    ):
        menu_logistica = "🚛 Transporte"
        submenu_logistica = "👨 Operadores"
        opcion_logistica = "📋 Consulta operador"


    if st.sidebar.button(
        "✏️ Editar operador",
        use_container_width=True
    ):
        menu_logistica = "🚛 Transporte"
        submenu_logistica = "👨 Operadores"
        opcion_logistica = "✏️ Editar operador"


    # ==========================================
    # RUTAS
    # ==========================================

    st.sidebar.markdown("### 📍 Rutas")


    if st.sidebar.button(
        "➕ Alta ruta",
        use_container_width=True
    ):
        menu_logistica = "📍 Rutas"
        submenu_logistica = "Rutas"
        opcion_logistica = "➕ Alta ruta"


    if st.sidebar.button(
        "❌ Baja ruta",
        use_container_width=True
    ):
        menu_logistica = "📍 Rutas"
        submenu_logistica = "Rutas"
        opcion_logistica = "❌ Baja ruta"


    if st.sidebar.button(
        "📋 Consulta ruta",
        use_container_width=True
    ):
        menu_logistica = "📍 Rutas"
        submenu_logistica = "Rutas"
        opcion_logistica = "📋 Consulta ruta"


    if st.sidebar.button(
        "✏️ Editar ruta",
        use_container_width=True
    ):
        menu_logistica = "📍 Rutas"
        submenu_logistica = "Rutas"
        opcion_logistica = "✏️ Editar ruta"


    # ==========================================
    # TRACKING
    # ==========================================

    st.sidebar.markdown("### 📡 Tracking")


    if st.sidebar.button(
        "📍 Seguimiento embarque",
        use_container_width=True
    ):
        menu_logistica = "📡 Tracking"
        submenu_logistica = "Tracking"
        opcion_logistica = "📍 Seguimiento embarque"


    if st.sidebar.button(
        "📋 Consulta tracking",
        use_container_width=True
    ):
        menu_logistica = "📡 Tracking"
        submenu_logistica = "Tracking"
        opcion_logistica = "📋 Consulta tracking"


    if st.sidebar.button(
        "🚨 Eventos logísticos",
        use_container_width=True
    ):
        menu_logistica = "📡 Tracking"
        submenu_logistica = "Tracking"
        opcion_logistica = "🚨 Eventos logísticos"


    return (
        menu_logistica,
        submenu_logistica,
        opcion_logistica
    )
