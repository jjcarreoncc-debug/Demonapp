import streamlit as st


def sidebar_logistica():

    # ==========================================
    # SESSION STATE
    # ==========================================

    if "menu_logistica" not in st.session_state:
        st.session_state.menu_logistica = "📦 Embarques"

    if "submenu_logistica" not in st.session_state:
        st.session_state.submenu_logistica = "Embarques"

    if "opcion_logistica" not in st.session_state:
        st.session_state.opcion_logistica = "➕ Alta embarque"

    # ==========================================
    # FUNCIÓN PARA CAMBIAR OPCIÓN
    # ==========================================

    def cambiar_opcion(menu, submenu, opcion):
        st.session_state.menu_logistica = menu
        st.session_state.submenu_logistica = submenu
        st.session_state.opcion_logistica = opcion

    # ==========================================
    # SIDEBAR
    # ==========================================

    st.sidebar.markdown("## 🚚 Logística")

    # ==========================================
    # INICIO
    # ==========================================

    if st.sidebar.button(
        "🏠 Inicio",
        use_container_width=True,
        key="log_btn_inicio"
    ):
        cambiar_opcion(
            "Inicio",
            "Inicio",
            "🏠 Inicio"
        )

    # ==========================================
    # EMBARQUES
    # ==========================================

    st.sidebar.markdown("### 📦 Embarques")

    if st.sidebar.button(
        "➕ Alta embarque",
        use_container_width=True,
        key="log_btn_alta_embarque"
    ):
        cambiar_opcion(
            "📦 Embarques",
            "Embarques",
            "➕ Alta embarque"
        )

    if st.sidebar.button(
        "✏️ Actualizar estatus embarque",
        use_container_width=True,
        key="log_btn_actualizar_estatus_embarque"
    ):
        cambiar_opcion(
            "📦 Embarques",
            "Embarques",
            "✏️ Actualizar estatus embarque"
        )

    if st.sidebar.button(
        "❌ Baja embarque",
        use_container_width=True,
        key="log_btn_baja_embarque"
    ):
        cambiar_opcion(
            "📦 Embarques",
            "Embarques",
            "❌ Baja embarque"
        )

    if st.sidebar.button(
        "📋 Consulta embarque",
        use_container_width=True,
        key="log_btn_consulta_embarque"
    ):
        cambiar_opcion(
            "📦 Embarques",
            "Embarques",
            "📋 Consulta embarque"
        )

    if st.sidebar.button(
        "📊 Dashboard embarques",
        use_container_width=True,
        key="log_btn_dashboard_embarques"
    ):
        cambiar_opcion(
            "📦 Embarques",
            "Embarques",
            "📊 Dashboard embarques"
        )

    if st.sidebar.button(
        "✏️ Editar embarque",
        use_container_width=True,
        key="log_btn_editar_embarque"
    ):
        cambiar_opcion(
            "📦 Embarques",
            "Embarques",
            "✏️ Editar embarque"
        )

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
        use_container_width=True,
        key="log_btn_alta_transportista"
    ):
        cambiar_opcion(
            "🚛 Transporte",
            "👥 Transportistas",
            "➕ Alta transportista"
        )

    if st.sidebar.button(
        "❌ Baja transportista",
        use_container_width=True,
        key="log_btn_baja_transportista"
    ):
        cambiar_opcion(
            "🚛 Transporte",
            "👥 Transportistas",
            "❌ Baja transportista"
        )

    if st.sidebar.button(
        "📋 Consulta transportista",
        use_container_width=True,
        key="log_btn_consulta_transportista"
    ):
        cambiar_opcion(
            "🚛 Transporte",
            "👥 Transportistas",
            "📋 Consulta transportista"
        )

    if st.sidebar.button(
        "✏️ Editar transportista",
        use_container_width=True,
        key="log_btn_editar_transportista"
    ):
        cambiar_opcion(
            "🚛 Transporte",
            "👥 Transportistas",
            "✏️ Editar transportista"
        )

    # ==========================================
    # VEHÍCULOS
    # ==========================================

    st.sidebar.markdown("#### 🚚 Vehículos")

    if st.sidebar.button(
        "➕ Alta vehículo",
        use_container_width=True,
        key="log_btn_alta_vehiculo"
    ):
        cambiar_opcion(
            "🚛 Transporte",
            "🚚 Vehículos",
            "➕ Alta vehículo"
        )

    if st.sidebar.button(
        "❌ Baja vehículo",
        use_container_width=True,
        key="log_btn_baja_vehiculo"
    ):
        cambiar_opcion(
            "🚛 Transporte",
            "🚚 Vehículos",
            "❌ Baja vehículo"
        )

    if st.sidebar.button(
        "📋 Consulta vehículo",
        use_container_width=True,
        key="log_btn_consulta_vehiculo"
    ):
        cambiar_opcion(
            "🚛 Transporte",
            "🚚 Vehículos",
            "📋 Consulta vehículo"
        )

    if st.sidebar.button(
        "✏️ Editar vehículo",
        use_container_width=True,
        key="log_btn_editar_vehiculo"
    ):
        cambiar_opcion(
            "🚛 Transporte",
            "🚚 Vehículos",
            "✏️ Editar vehículo"
        )

    # ==========================================
    # OPERADORES
    # ==========================================

    st.sidebar.markdown("#### 👨 Operadores")

    if st.sidebar.button(
        "➕ Alta operador",
        use_container_width=True,
        key="log_btn_alta_operador"
    ):
        cambiar_opcion(
            "🚛 Transporte",
            "👨 Operadores",
            "➕ Alta operador"
        )

    if st.sidebar.button(
        "❌ Baja operador",
        use_container_width=True,
        key="log_btn_baja_operador"
    ):
        cambiar_opcion(
            "🚛 Transporte",
            "👨 Operadores",
            "❌ Baja operador"
        )

    if st.sidebar.button(
        "📋 Consulta operador",
        use_container_width=True,
        key="log_btn_consulta_operador"
    ):
        cambiar_opcion(
            "🚛 Transporte",
            "👨 Operadores",
            "📋 Consulta operador"
        )

    if st.sidebar.button(
        "✏️ Editar operador",
        use_container_width=True,
        key="log_btn_editar_operador"
    ):
        cambiar_opcion(
            "🚛 Transporte",
            "👨 Operadores",
            "✏️ Editar operador"
        )

    # ==========================================
    # RUTAS
    # ==========================================

    st.sidebar.markdown("### 📍 Rutas")

    if st.sidebar.button(
        "➕ Alta ruta",
        use_container_width=True,
        key="log_btn_alta_ruta"
    ):
        cambiar_opcion(
            "📍 Rutas",
            "Rutas",
            "➕ Alta ruta"
        )

    if st.sidebar.button(
        "❌ Baja ruta",
        use_container_width=True,
        key="log_btn_baja_ruta"
    ):
        cambiar_opcion(
            "📍 Rutas",
            "Rutas",
            "❌ Baja ruta"
        )

    if st.sidebar.button(
        "📋 Consulta ruta",
        use_container_width=True,
        key="log_btn_consulta_ruta"
    ):
        cambiar_opcion(
            "📍 Rutas",
            "Rutas",
            "📋 Consulta ruta"
        )

    if st.sidebar.button(
        "✏️ Editar ruta",
        use_container_width=True,
        key="log_btn_editar_ruta"
    ):
        cambiar_opcion(
            "📍 Rutas",
            "Rutas",
            "✏️ Editar ruta"
        )

    # ==========================================
    # TRACKING
    # ==========================================

    st.sidebar.markdown("### 📡 Tracking")

    if st.sidebar.button(
        "📍 Seguimiento embarque",
        use_container_width=True,
        key="log_btn_seguimiento_embarque"
    ):
        cambiar_opcion(
            "📡 Tracking",
            "Tracking",
            "📍 Seguimiento embarque"
        )

    if st.sidebar.button(
        "📋 Consulta tracking",
        use_container_width=True,
        key="log_btn_consulta_tracking"
    ):
        cambiar_opcion(
            "📡 Tracking",
            "Tracking",
            "📋 Consulta tracking"
        )

    if st.sidebar.button(
        "🚨 Eventos logísticos",
        use_container_width=True,
        key="log_btn_eventos_logisticos"
    ):
        cambiar_opcion(
            "📡 Tracking",
            "Tracking",
            "🚨 Eventos logísticos"
        )

    return (
        st.session_state.menu_logistica,
        st.session_state.submenu_logistica,
        st.session_state.opcion_logistica
    )
