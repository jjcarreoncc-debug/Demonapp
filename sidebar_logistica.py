import streamlit as st


def set_opcion_logistica(menu, submenu, opcion):
    st.session_state.menu_logistica = menu
    st.session_state.submenu_logistica = submenu
    st.session_state.opcion_logistica = opcion


def boton_logistica(texto, key, menu, submenu, opcion):
    st.button(
        texto,
        use_container_width=True,
        key=key,
        on_click=set_opcion_logistica,
        args=(menu, submenu, opcion)
    )


def sidebar_logistica():

    with st.sidebar:

        st.markdown("## 🏢 SIGEM")
        st.markdown("### 🚚 Logística")
        st.markdown("---")

        if "menu_logistica" not in st.session_state:
            st.session_state.menu_logistica = "Embarques"

        if "submenu_logistica" not in st.session_state:
            st.session_state.submenu_logistica = "Gestión de embarques"

        if "opcion_logistica" not in st.session_state:
            st.session_state.opcion_logistica = "➕ Alta embarque"

        boton_logistica(
            "🏠 Inicio",
            "log_btn_inicio",
            "Inicio",
            "Inicio",
            "🏠 Inicio"
        )

        with st.expander("📦 Embarques", expanded=False):

            with st.expander("📋 Gestión de embarques", expanded=False):

                boton_logistica(
                    "➕ Alta embarque",
                    "log_btn_alta_embarque",
                    "Embarques",
                    "Gestión de embarques",
                    "➕ Alta embarque"
                )

                boton_logistica(
                    "✏️ Editar embarque",
                    "log_btn_editar_embarque",
                    "Embarques",
                    "Gestión de embarques",
                    "✏️ Editar embarque"
                )

                boton_logistica(
                    "❌ Baja embarque",
                    "log_btn_baja_embarque",
                    "Embarques",
                    "Gestión de embarques",
                    "❌ Baja embarque"
                )

                boton_logistica(
                    "📋 Consulta embarque",
                    "log_btn_consulta_embarque",
                    "Embarques",
                    "Gestión de embarques",
                    "📋 Consulta embarque"
                )

            with st.expander("🔄 Estatus y eventos", expanded=False):

                boton_logistica(
                    "✏️ Actualizar estatus embarque",
                    "log_btn_actualizar_estatus_embarque",
                    "Embarques",
                    "Estatus y eventos",
                    "✏️ Actualizar estatus embarque"
                )

                boton_logistica(
                    "🛰️ Eventos embarque",
                    "log_btn_eventos_embarque",
                    "Embarques",
                    "Estatus y eventos",
                    "🛰️ Eventos embarque"
                )

            with st.expander("📊 Consultas y dashboard", expanded=False):

                boton_logistica(
                    "📊 Dashboard embarques",
                    "log_btn_dashboard_embarques",
                    "Embarques",
                    "Consultas y dashboard",
                    "📊 Dashboard embarques"
                )

        with st.expander("🚛 Transporte", expanded=False):

            with st.expander("👥 Transportistas", expanded=False):

                boton_logistica(
                    "➕ Alta transportista",
                    "log_btn_alta_transportista",
                    "Transporte",
                    "Transportistas",
                    "➕ Alta transportista"
                )

                boton_logistica(
                    "❌ Baja transportista",
                    "log_btn_baja_transportista",
                    "Transporte",
                    "Transportistas",
                    "❌ Baja transportista"
                )

                boton_logistica(
                    "📋 Consulta transportista",
                    "log_btn_consulta_transportista",
                    "Transporte",
                    "Transportistas",
                    "📋 Consulta transportista"
                )

                boton_logistica(
                    "✏️ Editar transportista",
                    "log_btn_editar_transportista",
                    "Transporte",
                    "Transportistas",
                    "✏️ Editar transportista"
                )

            with st.expander("🚚 Vehículos", expanded=False):

                boton_logistica(
                    "➕ Alta vehículo",
                    "log_btn_alta_vehiculo",
                    "Transporte",
                    "Vehículos",
                    "➕ Alta vehículo"
                )

                boton_logistica(
                    "❌ Baja vehículo",
                    "log_btn_baja_vehiculo",
                    "Transporte",
                    "Vehículos",
                    "❌ Baja vehículo"
                )

                boton_logistica(
                    "📋 Consulta vehículo",
                    "log_btn_consulta_vehiculo",
                    "Transporte",
                    "Vehículos",
                    "📋 Consulta vehículo"
                )

                boton_logistica(
                    "✏️ Editar vehículo",
                    "log_btn_editar_vehiculo",
                    "Transporte",
                    "Vehículos",
                    "✏️ Editar vehículo"
                )

            with st.expander("👨 Operadores", expanded=False):

                boton_logistica(
                    "➕ Alta operador",
                    "log_btn_alta_operador",
                    "Transporte",
                    "Operadores",
                    "➕ Alta operador"
                )

                boton_logistica(
                    "❌ Baja operador",
                    "log_btn_baja_operador",
                    "Transporte",
                    "Operadores",
                    "❌ Baja operador"
                )

                boton_logistica(
                    "📋 Consulta operador",
                    "log_btn_consulta_operador",
                    "Transporte",
                    "Operadores",
                    "📋 Consulta operador"
                )

                boton_logistica(
                    "✏️ Editar operador",
                    "log_btn_editar_operador",
                    "Transporte",
                    "Operadores",
                    "✏️ Editar operador"
                )

        with st.expander("📍 Rutas", expanded=False):

            with st.expander("🗺️ Gestión de rutas", expanded=False):

                boton_logistica(
                    "➕ Alta ruta",
                    "log_btn_alta_ruta",
                    "Rutas",
                    "Gestión de rutas",
                    "➕ Alta ruta"
                )

                boton_logistica(
                    "❌ Baja ruta",
                    "log_btn_baja_ruta",
                    "Rutas",
                    "Gestión de rutas",
                    "❌ Baja ruta"
                )

                boton_logistica(
                    "📋 Consulta ruta",
                    "log_btn_consulta_ruta",
                    "Rutas",
                    "Gestión de rutas",
                    "📋 Consulta ruta"
                )

                boton_logistica(
                    "✏️ Editar ruta",
                    "log_btn_editar_ruta",
                    "Rutas",
                    "Gestión de rutas",
                    "✏️ Editar ruta"
                )

        with st.expander("📡 Tracking", expanded=False):

            with st.expander("📍 Seguimiento", expanded=False):

                boton_logistica(
                    "📍 Seguimiento embarque",
                    "log_btn_seguimiento_embarque",
                    "Tracking",
                    "Seguimiento",
                    "📍 Seguimiento embarque"
                )

                boton_logistica(
                    "📋 Consulta tracking",
                    "log_btn_consulta_tracking",
                    "Tracking",
                    "Seguimiento",
                    "📋 Consulta tracking"
                )

                boton_logistica(
                    "🚨 Eventos logísticos",
                    "log_btn_eventos_logisticos",
                    "Tracking",
                    "Seguimiento",
                    "🚨 Eventos logísticos"
                )

        with st.expander("🚨 Incidencias", expanded=False):

            with st.expander("📝 Gestión de incidencias", expanded=False):

                boton_logistica(
                    "➕ Alta incidencia",
                    "log_btn_alta_incidencia",
                    "Incidencias",
                    "Gestión de incidencias",
                    "➕ Alta incidencia"
                )

                boton_logistica(
                    "❌ Baja incidencia",
                    "log_btn_baja_incidencia",
                    "Incidencias",
                    "Gestión de incidencias",
                    "❌ Baja incidencia"
                )

                boton_logistica(
                    "📋 Consulta incidencia",
                    "log_btn_consulta_incidencia",
                    "Incidencias",
                    "Gestión de incidencias",
                    "📋 Consulta incidencia"
                )

                boton_logistica(
                    "✏️ Actualizar incidencia",
                    "log_btn_actualizar_incidencia",
                    "Incidencias",
                    "Gestión de incidencias",
                    "✏️ Actualizar incidencia"
                )

                boton_logistica(
                    "✅ Cerrar incidencia",
                    "log_btn_cerrar_incidencia",
                    "Incidencias",
                    "Gestión de incidencias",
                    "✅ Cerrar incidencia"
                )

            with st.expander("📊 Consultas y dashboard", expanded=False):

                boton_logistica(
                    "📊 Dashboard incidencias",
                    "log_btn_dashboard_incidencias",
                    "Incidencias",
                    "Consultas y dashboard",
                    "📊 Dashboard incidencias"
                )

    return (
        st.session_state.menu_logistica,
        st.session_state.submenu_logistica,
        st.session_state.opcion_logistica
    )
