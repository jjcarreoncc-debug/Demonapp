import streamlit as st


def sidebar_logistica():

    st.sidebar.markdown("## 🚚 Logística")

    menu_log = st.sidebar.radio(
        "Menú Logística",
        [
            "🏠 Inicio",
            "📦 Embarques",
            "🚛 Transporte",
            "📍 Rutas",
            "📡 Tracking",
            "🧾 Entregas",
            "📦 Inventario Logístico",
            "📊 Analytics"
        ]
    )

    submenu_log = None
    opcion_log = None

    if menu_log == "🏠 Inicio":
        submenu_log = "Inicio"
        opcion_log = "Resumen"

    elif menu_log == "📦 Embarques":
        submenu_log = st.sidebar.radio(
            "Embarques",
            [
                "➕ Generar embarque",
                "📦 Carga embarque",
                "📋 Consultar embarques",
                "✏️ Actualizar embarque",
                "🚨 Embarques pendientes"
            ]
        )
        opcion_log = submenu_log

    elif menu_log == "🚛 Transporte":
        submenu_log = st.sidebar.radio(
            "Transporte",
            [
                "🚚 Transportistas",
                "🚗 Vehículos",
                "👨‍✈️ Operadores",
                "⛽ Control transporte"
            ]
        )
        opcion_log = submenu_log

    elif menu_log == "📍 Rutas":
        submenu_log = st.sidebar.radio(
            "Rutas",
            [
                "➕ Crear ruta",
                "📋 Consultar rutas",
                "🗺️ Asignar rutas",
                "⏱️ Tiempos entrega"
            ]
        )
        opcion_log = submenu_log

    elif menu_log == "📡 Tracking":
        submenu_log = st.sidebar.radio(
            "Tracking",
            [
                "📍 Seguimiento embarque",
                "🕒 Eventos logísticos",
                "🚨 Retrasos",
                "📦 Tracking pedidos",
                "🧾 Historial tracking"
            ]
        )
        opcion_log = submenu_log

    elif menu_log == "🧾 Entregas":
        submenu_log = st.sidebar.radio(
            "Entregas",
            [
                "✅ Confirmar entrega",
                "📋 Historial entregas",
                "🚨 Entregas pendientes",
                "📄 Evidencias entrega"
            ]
        )
        opcion_log = submenu_log

    elif menu_log == "📦 Inventario Logístico":
        submenu_log = st.sidebar.radio(
            "Inventario Logístico",
            [
                "📤 Salidas embarque",
                "📦 Material embarcado",
                "🏭 Bodega despacho",
                "📋 Trazabilidad logística"
            ]
        )
        opcion_log = submenu_log

    elif menu_log == "📊 Analytics":
        submenu_log = st.sidebar.radio(
            "Analytics",
            [
                "📊 Dashboard logística",
                "🚚 Utilización transporte",
                "⏱️ Entregas a tiempo",
                "🚨 Retrasos",
                "📈 Productividad logística",
                "📍 Tracking analytics",
                "💰 Costos logísticos"
            ]
        )
        opcion_log = submenu_log

    return menu_log, submenu_log, opcion_log
