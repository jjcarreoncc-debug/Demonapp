import streamlit as st
import pandas as pd

from logistica_dashboard_app import dashboard_logistica
from logistica_indicadores_app import indicadores_logistica_app


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
    # MENÚ
    # =========================
    if st.session_state.logistica_vista == "menu":

        c1, c2, c3, c4 = st.columns(4)

        if c1.button("📊 Dashboard"):
            st.session_state.logistica_vista = "dashboard"
            st.rerun()

        if c2.button("🏬 Bodegas"):
            st.session_state.logistica_vista = "bodegas"
            st.rerun()

        if c3.button("🚛 Tránsito"):
            st.session_state.logistica_vista = "transito"
            st.rerun()

        if c4.button("🚚 Transportistas"):
            st.session_state.logistica_vista = "transportistas"
            st.rerun()

        c5, c6, c7, c8 = st.columns(4)

        if c5.button("🛣️ Rutas"):
            st.session_state.logistica_vista = "rutas"
            st.rerun()

        if c6.button("📥 Recepción"):
            st.session_state.logistica_vista = "recepcion"
            st.rerun()

        if c7.button("📤 Despachos"):
            st.session_state.logistica_vista = "despachos"
            st.rerun()

        if c8.button("📋 Detalle"):
            st.session_state.logistica_vista = "detalle"
            st.rerun()

        c9, _, _, _ = st.columns(4)

        if c9.button("📊 Indicadores"):
            st.session_state.logistica_vista = "indicadores"
            st.rerun()

    # =========================
    # VOLVER
    # =========================
    if st.session_state.logistica_vista != "menu":

        if st.button("🔙 Volver"):
            st.session_state.logistica_vista = "menu"
            st.rerun()

    # =========================
    # VISTAS
    # =========================
    if st.session_state.logistica_vista == "dashboard":

        dashboard_logistica(
            transito,
            bodegas,
            transportistas
        )

    elif st.session_state.logistica_vista == "bodegas":

        st.subheader("🏬 Bodegas")
        st.dataframe(bodegas, use_container_width=True)

    elif st.session_state.logistica_vista == "transito":

        st.subheader("🚛 Tránsito")
        st.dataframe(transito, use_container_width=True)

    elif st.session_state.logistica_vista == "transportistas":

        st.subheader("🚚 Transportistas")
        st.dataframe(transportistas, use_container_width=True)

    elif st.session_state.logistica_vista == "rutas":

        st.subheader("🛣️ Rutas")
        st.dataframe(rutas, use_container_width=True)

    elif st.session_state.logistica_vista == "recepcion":

        st.subheader("📥 Recepción")
        st.dataframe(recepcion, use_container_width=True)

    elif st.session_state.logistica_vista == "despachos":

        st.subheader("📤 Despachos")
        st.dataframe(despachos, use_container_width=True)

    elif st.session_state.logistica_vista == "detalle":

        st.subheader("📋 Detalle General")
        st.dataframe(transito, use_container_width=True)

    elif st.session_state.logistica_vista == "indicadores":

        indicadores_logistica_app(
            transito,
            recepcion,
            despachos,
            transportistas,
            rutas
        )
