import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

from sigem_db import get_db_path


st.set_page_config(
    layout="wide"
)


# =====================================================
# CONEXION
# =====================================================

def get_connection():

    conn = sqlite3.connect(
        get_db_path("logistica")
    )

    return conn


# =====================================================
# ESTILOS
# =====================================================

def aplicar_estilos():

    st.markdown(
        """
        <style>

        .block-container {
            padding-top: 1rem;
            padding-left: 2rem;
            padding-right: 2rem;
            max-width: 100%;
        }

        .titulo-app {
            font-size: 36px;
            font-weight: 900;
            color: #1F4E79;
            margin-bottom: 0px;
        }

        .subtitulo-app {
            font-size: 15px;
            color: #5B6575;
            margin-bottom: 20px;
        }

        .filtros-titulo {
            font-size: 25px;
            font-weight: 800;
            color: #111827;
            margin-bottom: 16px;
        }

        div[data-testid="metric-container"] {
            background: #FFFFFF;
            border: 1px solid #D1D5DB;
            padding: 16px;
            border-radius: 16px;
            box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
        }

        .badge {
            padding: 5px 10px;
            border-radius: 12px;
            font-weight: 700;
            font-size: 13px;
            display: inline-block;
        }

        .badge-pendiente {
            background: #FEF3C7;
            color: #92400E;
        }

        .badge-cargada {
            background: #DCFCE7;
            color: #166534;
        }

        .badge-cancelada {
            background: #FEE2E2;
            color: #991B1B;
        }

        .badge-transito {
            background: #DBEAFE;
            color: #1E40AF;
        }

        </style>
        """,
        unsafe_allow_html=True
    )


# =====================================================
# UTILERIAS
# =====================================================

def tabla_existe(conn, tabla):

    try:

        df = pd.read_sql_query(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name = ?
            """,
            conn,
            params=(tabla,)
        )

        return not df.empty

    except Exception:

        return False


def formatear_estatus(estatus):

    estatus_txt = str(estatus).strip()

    estatus_low = estatus_txt.lower()

    if "cancel" in estatus_low:
        return "🔴 Cancelada"

    if "carg" in estatus_low:
        return "🟢 Cargada"

    if "tránsito" in estatus_low or "transito" in estatus_low:
        return "🔵 En tránsito"

    if "pend" in estatus_low:
        return "🟡 Pendiente"

    if estatus_txt == "":
        return "⚪ Sin estatus"

    return estatus_txt


def formatear_tr(codigo_transporte):

    tr = str(codigo_transporte).strip()

    if tr == "" or tr.lower() == "none":
        return "⚪ Sin TR"

    return f"🚛 {tr}"


# =====================================================
# OBTENER HOJAS DE CARGA
# =====================================================

def obtener_hojas_carga():

    conn = get_connection()

    if not tabla_existe(conn, "hojas_carga"):

        conn.close()

        return pd.DataFrame()

    existe_embarques = tabla_existe(
        conn,
        "embarques"
    )

    if existe_embarques:

        query = """
            SELECT
                h.folio_hoja_carga,
                h.cliente,
                h.destino,
                h.pedido,
                h.folios_entrega,
                h.fecha_creacion,
                h.estatus_hoja,
                h.total_entregas,
                h.total_materiales,
                h.total_piezas,
                h.total_cajas,
                h.total_tarimas,
                h.peso_total,
                h.volumen_total,
                h.observaciones,
                h.usuario,

                e.folio_embarque,
                e.codigo_transporte,
                e.transportista,
                e.vehiculo,
                e.placas,
                e.operador,
                e.ruta,
                e.estatus AS estatus_embarque

            FROM hojas_carga h

            LEFT JOIN embarques e
                ON h.folio_hoja_carga = e.folio_hoja_carga

            ORDER BY
                h.fecha_creacion DESC,
                h.folio_hoja_carga DESC
        """

    else:

        query = """
            SELECT
                h.folio_hoja_carga,
                h.cliente,
                h.destino,
                h.pedido,
                h.folios_entrega,
                h.fecha_creacion,
                h.estatus_hoja,
                h.total_entregas,
                h.total_materiales,
                h.total_piezas,
                h.total_cajas,
                h.total_tarimas,
                h.peso_total,
                h.volumen_total,
                h.observaciones,
                h.usuario,

                '' AS folio_embarque,
                '' AS codigo_transporte,
                '' AS transportista,
                '' AS vehiculo,
                '' AS placas,
                '' AS operador,
                '' AS ruta,
                '' AS estatus_embarque

            FROM hojas_carga h

            ORDER BY
                h.fecha_creacion DESC,
                h.folio_hoja_carga DESC
        """

    df = pd.read_sql_query(
        query,
        conn
    )

    conn.close()

    return df

# =====================================================
# APP
# =====================================================

def consulta_hoja_carga_app():

    aplicar_estilos()

    st.markdown(
        '<div class="titulo-app">📦 Centro operativo de hojas de carga</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitulo-app">Consulta operativa de hojas de carga, TR y detalle logístico.</div>',
        unsafe_allow_html=True
    )

    df = obtener_hojas_carga()

    if df.empty:

        st.warning(
            "No existen hojas de carga registradas."
        )

        return

    st.success(
        "✅ Módulo conectado correctamente."
    )

    st.dataframe(
        df,
        use_container_width=True,
        height=500
    )


# =====================================================
# EJECUCION
# =====================================================

if __name__ == "__main__":

    consulta_hoja_carga_app()
