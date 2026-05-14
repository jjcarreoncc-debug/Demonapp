import streamlit as st


def set_opcion_logistica(menu, submenu, opcion):
    st.session_state.menu_logistica = menu
    st.session_state.submenu_logistica = submenu
    st.session_state.opcion_logistica = opcion


def sidebar_logistica():

    with st.sidebar:

        st.markdown("## 🏢 SIGEM")
        st.markdown("### 🚚 Logística")
        st.markdown("---")

        # ==========================================
        # SESSION STATE
        # ==========================================

        if "menu_logistica" not in st.session_state:
            set_opcion_logistica(
                "Embarques",
                "Gestión de embarques",
                "➕ Alta embarque"
            )

        # ==========================================
        # INICIO
        # ==========================================

        if st.button(
            "🏠 Inicio",
            use_container_width=True,
            key="log_btn_inicio"
        ):
            set_opcion_logistica(
                "Inicio",
                "Inicio",
                "🏠 Inicio"
            )

        # ==========================================
        # EMBARQUES
        # ==========================================

        with st.expander("📦 Embarques", expanded=True):

            with st.expander("📋 Gestión de embarques", expanded=True):

                if st.button(
                    "➕ Alta embarque",
                    use_container_width=True,
                    key="log_btn_alta_embarque"
                ):
                    set_opcion_logistica(
                        "Embarques",
                        "Gestión de embarques",
                        "➕ Alta embarque"
                    )

                if st.button(
                    "✏️ Editar embarque",
                    use_container_width=True,
                    key="log_btn_editar_embarque"
                ):
                    set_opcion_logistica(
                        "Embarques",
                        "Gestión de embarques",
                        "✏️ Editar embarque"
                    )

                if st.button(
                    "❌ Baja embarque",
                    use_container_width=True,
                    key="log_btn_baja_embarque"
                ):
                    set_opcion_logistica(
                        "Embarques",
                        "Gestión de embarques",
                        "❌ Baja embarque"
                    )

                if st.button(
                    "📋 Consulta embarque",
                    use_container_width=True,
                    key="log_btn_consulta_embarque"
                ):
                    set_opcion_logistica(
                        "Embarques",
                        "Gestión de embarques",
                        "📋 Consulta embarque"
                    )

            with st.expander("🔄 Estatus y eventos"):

                if st.button(
                    "✏️ Actualizar estatus embarque",
                    use_container_width=True,
                    key="log_btn_actualizar_estatus_embarque"
                ):
                    set_opcion_logistica(
                        "Embarques",
                        "Estatus y eventos",
                        "✏️ Actualizar estatus embarque"
                    )

                if st.button(
                    "🛰️ Eventos embarque",
                    use_container_width=True,
                    key="log_btn_eventos_embarque"
                ):
                    set_opcion_logistica(
                        "Embarques",
                        "Estatus y eventos",
                        "🛰️ Eventos embarque"
                    )

            with st.expander("📊 Consultas y dashboard"):

                if st.button(
                    "📊 Dashboard embarques",
                    use_container_width=True,
                    key="log_btn_dashboard_embarques"
                ):
                    set_opcion_logistica(
                        "Embarques",
                        "Consultas y dashboard",
                        "📊 Dashboard embarques"
                    )

        # ==========================================
        # TRANSPORTE
        # ==========================================

        with st.expander("🚛 Transporte"):

            with st.expander("👥 Transportistas"):

                if st.button(
                    "➕ Alta transportista",
                    use_container_width=True,
                    key="log_btn_alta_transportista"
                ):
                    set_opcion_logistica(
                        "Transporte",
                        "Transportistas",
                        "➕ Alta transportista"
                    )

                if st.button(
                    "❌ Baja transportista",
                    use_container_width=True,
                    key="log_btn_baja_transportista"
                ):
                    set_opcion_logistica(
                        "Transporte",
                        "Transportistas",
                        "❌ Baja transportista"
                    )

                if st.button(
                    "📋 Consulta transportista",
                    use_container_width=True,
                    key="log_btn_consulta_transportista"
                ):
                    set_opcion_logistica(
                        "Transporte",
                        "Transportistas",
                        "📋 Consulta transportista"
                    )

                if st.button(
                    "✏️ Editar transportista",
                    use_container_width=True,
                    key="log_btn_editar_transportista"
                ):
                    set_opcion_logistica(
                        "Transporte",
                        "Transportistas",
                        "✏️ Editar transportista"
                    )

            with st.expander("🚚 Vehículos"):

                if st.button(
                    "➕ Alta vehículo",
                    use_container_width=True,
                    key="log_btn_alta_vehiculo"
                ):
                    set_opcion_logistica(
                        "Transporte",
                        "Vehículos",
                        "➕ Alta vehículo"
                    )

                if st.button(
                    "❌ Baja vehículo",
                    use_container_width=True,
                    key="log_btn_baja_vehiculo"
                ):
                    set_opcion_logistica(
                        "Transporte",
                        "Vehículos",
                        "❌ Baja vehículo"
                    )

                if st.button(
                    "📋 Consulta vehículo",
                    use_container_width=True,
                    key="log_btn_consulta_vehiculo"
                ):
                    set_opcion_logistica(
                        "Transporte",
                        "Vehículos",
                        "📋 Consulta vehículo"
                    )

                if st.button(
                    "✏️ Editar vehículo",
                    use_container_width=True,
                    key="log_btn_editar_vehiculo"
                ):
                    set_opcion_logistica(
                        "Transporte",
                        "Vehículos",
                        "✏️ Editar vehículo"
                    )

            with st.expander("👨 Operadores"):

                if st.button(
                    "➕ Alta operador",
                    use_container_width=True,
                    key="log_btn_alta_operador"
                ):
                    set_opcion_logistica(
                        "Transporte",
                        "Operadores",
                        "➕ Alta operador"
                    )

                if st.button(
                    "❌ Baja operador",
                    use_container_width=True,
                    key="log_btn_baja_operador"
                ):
                    set_opcion_logistica(
                        "Transporte",
                        "Operadores",
                        "❌ Baja operador"
                    )

                if st.button(
                    "📋 Consulta operador",
                    use_container_width=True,
                    key="log_btn_consulta_operador"
                ):
                    set_opcion_logistica(
                        "Transporte",
                        "Operadores",
                        "📋 Consulta operador"
                    )

                if st.button(
                    "✏️ Editar operador",
                    use_container_width=True,
                    key="log_btn_editar_operador"
                ):
                    set_opcion_logistica(
                        "Transporte",
                        "Operadores",
                        "✏️ Editar operador"
                    )

        # ==========================================
        # RUTAS
        # ==========================================

        with st.expander("📍 Rutas"):

            with st.expander("🗺️ Gestión de rutas"):

                if st.button(
                    "➕ Alta ruta",
                    use_container_width=True,
                    key="log_btn_alta_ruta"
                ):
                    set_opcion_logistica(
                        "Rutas",
                        "Gestión de rutas",
                        "➕ Alta ruta"
                    )

                if st.button(
                    "❌ Baja ruta",
                    use_container_width=True,
                    key="log_btn_baja_ruta"
                ):
                    set_opcion_logistica(
                        "Rutas",
                        "Gestión de rutas",
                        "❌ Baja ruta"
                    )

                if st.button(
                    "📋 Consulta ruta",
                    use_container_width=True,
                    key="log_btn_consulta_ruta"
                ):
                    set_opcion_logistica(
                        "Rutas",
                        "Gestión de rutas",
                        "📋 Consulta ruta"
                    )

                if st.button(
                    "✏️ Editar ruta",
                    use_container_width=True,
                    key="log_btn_editar_ruta"
                ):
                    set_opcion_logistica(
                        "Rutas",
                        "Gestión de rutas",
                        "✏️ Editar ruta"
                    )

        # ==========================================
        # TRACKING
        # ==========================================

        with st.expander("📡 Tracking"):

            with st.expander("📍 Seguimiento"):

                if st.button(
                    "📍 Seguimiento embarque",
                    use_container_width=True,
                    key="log_btn_seguimiento_embarque"
                ):
                    set_opcion_logistica(
                        "Tracking",
                        "Seguimiento",
                        "📍 Seguimiento embarque"
                    )

                if st.button(
                    "📋 Consulta tracking",
                    use_container_width=True,
                    key="log_btn_consulta_tracking"
                ):
                    set_opcion_logistica(
                        "Tracking",
                        "Seguimiento",
                        "📋 Consulta tracking"
                    )

                if st.button(
                    "🚨 Eventos logísticos",
                    use_container_width=True,
                    key="log_btn_eventos_logisticos"
                ):
                    set_opcion_logistica(
                        "Tracking",
                        "Seguimiento",
                        "🚨 Eventos logísticos"
                    )

        # ==========================================
        # INCIDENCIAS
        # ==========================================

        with st.expander("🚨 Incidencias"):

            with st.expander("📝 Gestión de incidencias"):

                if st.button(
                    "➕ Alta incidencia",
                    use_container_width=True,
                    key="log_btn_alta_incidencia"
                ):
                    set_opcion_logistica(
                        "Incidencias",
                        "Gestión de incidencias",
                        "➕ Alta incidencia"
                    )

                if st.button(
                    "❌ Baja incidencia",
                    use_container_width=True,
                    key="log_btn_baja_incidencia"
                ):
                    set_opcion_logistica(
                        "Incidencias",
                        "Gestión de incidencias",
                        "❌ Baja incidencia"
                    )

                if st.button(
                    "📋 Consulta incidencia",
                    use_container_width=True,
                    key="log_btn_consulta_incidencia"
                ):
                    set_opcion_logistica(
                        "Incidencias",
                        "Gestión de incidencias",
                        "📋 Consulta incidencia"
                    )

                if st.button(
                    "✏️ Actualizar incidencia",
                    use_container_width=True,
                    key="log_btn_actualizar_incidencia"
                ):
                    set_opcion_logistica(
                        "Incidencias",
                        "Gestión de incidencias",
                        "✏️ Actualizar incidencia"
                    )

                if st.button(
                    "✅ Cerrar incidencia",
                    use_container_width=True,
                    key="log_btn_cerrar_incidencia"
                ):
                    set_opcion_logistica(
                        "Incidencias",
                        "Gestión de incidencias",
                        "✅ Cerrar incidencia"
                    )

            with st.expander("📊 Consultas y dashboard"):

                if st.button(
                    "📊 Dashboard incidencias",
                    use_container_width=True,
                    key="log_btn_dashboard_incidencias"
                ):
                    set_opcion_logistica(
                        "Incidencias",
                        "Consultas y dashboard",
                        "📊 Dashboard incidencias"
                    )

    return (
        st.session_state.menu_logistica,
        st.session_state.submenu_logistica,
        st.session_state.opcion_logistica
    )
