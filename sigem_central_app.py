import streamlit as st
import pandas as pd
import sqlite3

from sigem_db import get_db_path

from auth_app import login_app, logout_app
from Minventarios_app import inventarios_app
from sidebar_analitico import analitico_app
from mantenimiento_app import mantenimiento_app
from Mlogistica_app import logistica_app


# =====================================================
# ESTILO GLOBAL ERP
# =====================================================

st.markdown(
    """
    <style>

    /* =====================================================
       SIDEBAR
    ===================================================== */

    section[data-testid="stSidebar"] {
        background-color: #dbeafe;
    }

    section[data-testid="stSidebar"] .block-container {
        padding-top: 0.3rem;
        padding-bottom: 0rem;
    }

    div.stButton > button {
        padding-top: 0.1rem;
        padding-bottom: 0.1rem;
    }

    hr {
        margin-top: 0.3rem;
        margin-bottom: 0.3rem;
    }

    /* =====================================================
       DATAFRAMES / GRIDS
    ===================================================== */

    .stDataFrame thead tr th {

        background-color: #dbeafe !important;

        color: #1e293b !important;

        font-weight: 700 !important;

        border: 1px solid #cbd5e1 !important;
    }

    .stDataFrame tbody tr td {

        background-color: white !important;

        color: #334155 !important;

        border: 1px solid #e2e8f0 !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =====================================================
# LOGIN
# =====================================================

if "autenticado" not in st.session_state:

    st.session_state.autenticado = False

if "rol" not in st.session_state:

    st.session_state.rol = None

if not st.session_state.autenticado:

    login_app()

    st.stop()

logout_app()


# =====================================================
# MODULO DEFAULT
# =====================================================

if "ruta_central" not in st.session_state:

    st.session_state.ruta_central = "inventarios"


# =====================================================
# SIDEBAR CENTRAL
# =====================================================

with st.sidebar:

    # =================================================
    # CONEXION SEGURIDAD
    # =================================================

    db_path = get_db_path("seguridad")

    conn = sqlite3.connect(db_path)

    usuario_actual = st.session_state.get(
        "usuario",
        ""
    )

    # =================================================
    # MODULOS POR ROL
    # =================================================

    query_modulos = """
        SELECT DISTINCT

            m.nombre_modulo,
            m.ruta,
            m.icono,
            m.orden_menu

        FROM usuarios u

        INNER JOIN roles r
            ON u.id_rol = r.id_rol

        INNER JOIN permisos_roles pr
            ON r.id_rol = pr.id_rol

        INNER JOIN modulos m
            ON pr.id_modulo = m.id_modulo

        WHERE u.usuario = ?
        AND m.activo = 1

        ORDER BY m.orden_menu
    """

    modulos_df = pd.read_sql_query(
        query_modulos,
        conn,
        params=(usuario_actual,)
    )

    conn.close()
    
    # =================================================
    # DICCIONARIO MODULOS
    # =================================================

    modulos_dict = {}

    for _, row in modulos_df.iterrows():

        label = f"{row['icono']} {row['nombre_modulo']}"

        modulos_dict[label] = row["ruta"]

    # =================================================
    # VALIDAR MODULOS
    # =================================================

    if len(modulos_dict) == 0:

        st.warning(
            "No tienes módulos asignados."
        )

        st.stop()

    # =================================================
    # VALIDAR RUTA ACTUAL
    # =================================================

    rutas_disponibles = list(
        modulos_dict.values()
    )

    if (
        st.session_state.ruta_central
        not in rutas_disponibles
    ):

        st.session_state.ruta_central = (
            rutas_disponibles[0]
        )

    # =================================================
    # LABEL ACTUAL
    # =================================================

    label_actual = list(
        modulos_dict.keys()
    )[0]

    for label, ruta in modulos_dict.items():

        if ruta == st.session_state.ruta_central:

            label_actual = label

            break

    # =================================================
    # RADIO MODULOS
    # =================================================

    modulo_sel = st.radio(
        "Módulos",
        list(modulos_dict.keys()),
        index=list(modulos_dict.keys()).index(
            label_actual
        ),
        key="menu_central_sigem"
    )

    # =================================================
    # GUARDAR RUTA
    # =================================================

    st.session_state.ruta_central = (
        modulos_dict[modulo_sel]
    )

    st.markdown("---")

    st.caption(
        f"👤 {st.session_state.get('nombre', '')}"
    )

    st.caption("SIGEM ERP")


# =====================================================
# ROUTER CENTRAL
# =====================================================

# =====================================================
# ROUTER CENTRAL
# =====================================================

ruta_central = st.session_state.get(
    "ruta_central",
    ""
)

if ruta_central == "inventarios":

    inventarios_app()

elif ruta_central == "datos_maestros":

    inventarios_app()

elif ruta_central == "operacion_inventario":

    inventarios_app()

elif ruta_central == "operacion_logistica":

    inventarios_app()

elif ruta_central == "consulta_analiticos":

    inventarios_app()

elif ruta_central == "inventario_fisico":

    inventarios_app()

elif ruta_central == "logistica":

    logistica_app()

elif ruta_central == "analitico":

    analitico_app()

elif ruta_central == "mantenimiento":

    mantenimiento_app()

else:

    st.info(
        "Selecciona un módulo del menú lateral para comenzar."
    )
# =====================================================
# ROUTER CENTRAL
# =====================================================
