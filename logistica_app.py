import streamlit as st
import pandas as pd

from logistica_dashboard_app import dashboard_logistica
from logistica_indicadores_app import indicadores_logistica_app
from logistica_operativa_app import logistica_operativa_app
from logistica_graficas_app import logistica_graficas_app
from logistica_filtros_app import filtros_logistica
from logistica_aplicar_filtros import aplicar_filtros_logistica


# =========================
# CSS LOGÍSTICA
# =========================
def aplicar_css_logistica():

    st.markdown("""
    <style>

    div.stButton > button {
        width: 100%;
        height: 70px;
        font-size: 16px;
        font-weight: bold;
        border-radius: 12px;
        border: none;
        background-color: #1f77b4;
        color: white;
    }

    div.stButton > button:hover {
        background-color: #145a86;
        color: white;
    }

    section[data-testid="stFileUploader"] {
        background-color: #f5f7fa;
        padding: 16px;
        border-radius: 14px;
        border-left: 6px solid #1f77b4;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.08);
        margin-bottom: 18px;
    }

    </style>
    """, unsafe_allow_html=True)


# =========================
# ESTRUCTURA ARCHIVOS
# =========================
def estructura_archivos_logistica():

    st.info("📌 Los archivos Excel deben venir en forma horizontal.")

    with st.expander("📄 Estructura requerida archivos Logística"):

        st.markdown("""
        **TRANSITO**  
        `ID_TRANSITO | FECHA_SALIDA | FECHA_ESTIMADA | FECHA_LLEGADA | NUMERO_PRODUCTO | CANTIDAD | ID_ORIGEN | ID_DESTINO | ID_TRANSPORTISTA | ESTADO_TRANSITO`

        **BODEGAS**  
        `ID_BODEGA | NOMBRE_BODEGA | CIUDAD | REGION | CAPACIDAD_MAX | TIPO_BODEGA | ESTADO_BODEGA`

        **TRANSPORTISTAS**  
        `ID_TRANSPORTISTA | NOMBRE_TRANSPORTISTA | TIPO_TRANSPORTE | PLACA | CONDUCTOR | TELEFONO | COSTO_FLETE | ESTADO_TRANSPORTISTA`

        **RUTAS**  
        `ID_RUTA | ID_ORIGEN | ID_DESTINO | CIUDAD_ORIGEN | CIUDAD_DESTINO | KM_RUTA | TIEMPO_ESTIMADO | COSTO_ESTIMADO`

        **RECEPCION**  
        `ID_RECEPCION | ID_TRANSITO | FECHA_RECEPCION | NUMERO_PRODUCTO | CANTIDAD_ESPERADA | CANTIDAD_RECIBIDA | DIFERENCIA | ESTADO_RECEPCION`

        **DESPACHOS**  
        `ID_DESPACHO | FECHA_DESPACHO | NUMERO_PRODUCTO | CANTIDAD | ID_BODEGA | DESTINO_CLIENTE | ID_TRANSPORTISTA | ESTADO_DESPACHO`
        """)


# =========================
# APP LOGÍSTICA
# =========================
def logistica_app():

    aplicar_css_logistica()

    st.title("🚚 Logística")

    estructura_archivos_logistica()

    if "logistica_vista" not in st.session_state:
        st.session_state.logistica_vista = "menu"

    if st.button("🏠 Ir al menú principal"):
        st.session_state.logistica_vista = "menu"
        st.rerun()

    # =========================
    # FILES
    # =========================
    archivo_transito = st.file_uploader(
        "🚛 Tránsito",
        type=["xlsx"],
        key="transito_file"
    )

    archivo_bodegas = st.file_uploader(
        "🏬 Bodegas",
        type=["xlsx"],
        key="bodegas_file_log"
    )

    archivo_transportistas = st.file_uploader(
        "🚚 Transportistas",
        type=["xlsx"],
        key="transportistas_file"
    )

    archivo_rutas = st.file_uploader(
        "🛣️ Rutas",
        type=["xlsx"],
        key="rutas_file"
    )

    archivo_recepcion = st.file_uploader(
        "📥 Recepción",
        type=["xlsx"],
        key="recepcion_file"
    )

    archivo_despachos = st.file_uploader(
        "📤 Despachos",
        type=["xlsx"],
        key="despachos_file"
    )

    # =========================
    # SESSION
    # =========================
    if archivo_transito:
        st.session_state.df_transito = pd.read_excel(archivo_transito)

    if archivo_bodegas:
        st.session_state.df_bodegas_log = pd.read_excel(archivo_bodegas)

    if archivo_transportistas:
        st.session_state.df_transportistas = pd.read_excel(archivo_transportistas)

    if archivo_rutas:
        st.session_state.df_rutas = pd.read_excel(archivo_rutas)

    if archivo_recepcion:
        st.session_state.df_recepcion = pd.read_excel(archivo_recepcion)

    if archivo_despachos:
        st.session_state.df_despachos = pd.read_excel(archivo_despachos)

    transito = st.session_state.get("df_transito")
    bodegas = st.session_state.get("df_bodegas_log")
    transportistas = st.session_state.get("df_transportistas")
    rutas = st.session_state.get("df_rutas")
    recepcion = st.session_state.get("df_recepcion")
    despachos = st.session_state.get("df_despachos")

    if (
        transito is None
        or bodegas is None
        or transportistas is None
        or rutas is None
        or recepcion is None
        or despachos is None
    ):
        st.warning("⚠️ Carga todos los archivos Excel de Logística")
        return

    # =========================
    # FILTROS
    # =========================
    filtros = filtros_logistica(
        transito,
        recepcion,
        despachos
    )

    # =========================
    # APLICAR FILTROS
    # =========================
    (
        transito_filtrado,
        recepcion_filtrado,
        despachos_filtrado
    ) = aplicar_filtros_logistica(
        transito,
        recepcion,
        despachos,
        filtros
    )

    # =========================
    # MENÚ PRINCIPAL
    # =========================
    if st.session_state.logistica_vista == "menu":

        st.subheader("Menú principal")

        c1, c2, c3, c4 = st.columns(4)

        if c1.button("📊 Dashboard Ejecutivo"):
            st.session_state.logistica_vista = "dashboard_ejecutivo"
            st.rerun()

        if c2.button("📦 Operación"):
            st.session_state.logistica_vista = "operacion"
            st.rerun()

        if c3.button("⚠️ Riesgos"):
            st.session_state.logistica_vista = "riesgos"
            st.rerun()

        if c4.button("📈 Analítica"):
            st.session_state.logistica_vista = "analitica"
            st.rerun()

    # =========================
    # VOLVER
    # =========================
    if st.session_state.logistica_vista != "menu":

        if st.button("🔙 Volver"):
            st.session_state.logistica_vista = "menu"
            st.rerun()

    # =========================
    # DASHBOARD EJECUTIVO
    # =========================
    if st.session_state.logistica_vista == "dashboard_ejecutivo":

        tab1, tab2, tab3 = st.tabs([
            "📊 Resumen",
            "📌 Indicadores",
            "📈 Gráficas"
        ])

        with tab1:
            dashboard_logistica(
                transito_filtrado,
                bodegas,
                transportistas
            )

        with tab2:
            indicadores_logistica_app(
                transito_filtrado,
                bodegas,
                transportistas,
                recepcion_filtrado,
                despachos_filtrado,
                rutas
            )

        with tab3:
            logistica_graficas_app(
                transito_filtrado,
                recepcion_filtrado,
                despachos_filtrado,
                transportistas,
                rutas
            )

    # =========================
    # OPERACIÓN
    # =========================
    elif st.session_state.logistica_vista == "operacion":

        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "🚛 Tránsito",
            "🏬 Bodegas",
            "🚚 Transportistas",
            "🛣️ Rutas",
            "📥 Recepción",
            "📤 Despachos",
            "⚙️ Operativo"
        ])

        with tab1:
            st.subheader("🚛 Tránsito")
            st.dataframe(transito_filtrado, use_container_width=True)

        with tab2:
            st.subheader("🏬 Bodegas")
            st.dataframe(bodegas, use_container_width=True)

        with tab3:
            st.subheader("🚚 Transportistas")
            st.dataframe(transportistas, use_container_width=True)

        with tab4:
            st.subheader("🛣️ Rutas")
            st.dataframe(rutas, use_container_width=True)

        with tab5:
            st.subheader("📥 Recepción")
            st.dataframe(recepcion_filtrado, use_container_width=True)

        with tab6:
            st.subheader("📤 Despachos")
            st.dataframe(despachos_filtrado, use_container_width=True)

        with tab7:
            logistica_operativa_app(
                transito_filtrado,
                recepcion_filtrado,
                despachos_filtrado,
                transportistas,
                rutas
            )

    # ==========================
    # RIESGOS
    # =========================
    elif st.session_state.logistica_vista == "riesgos":

        st.subheader("⚠️ Riesgos")
        st.warning("Módulo de riesgos en construcción.")

    # =========================
    # ANALÍTICA
    # =========================
    elif st.session_state.logistica_vista == "analitica":

    from logistica_analitica_app import logistica_analitica_app

    logistica_analitica_app(
        transito_filtrado,
        recepcion_filtrado,
        despachos_filtrado,
        transportistas,
        rutas
    )

        st.subheader("📈 Analítica")
        st.info("Módulo analítico en construcción.")
