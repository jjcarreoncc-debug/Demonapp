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

    # =====================================================
    # FORMATEOS
    # =====================================================

    df["estatus_visual"] = df["estatus_hoja"].apply(
        formatear_estatus
    )

    df["tr_visual"] = df["codigo_transporte"].apply(
        formatear_tr
    )

    # =====================================================
    # LAYOUT
    # =====================================================

    col_filtros, col_contenido = st.columns(
        [1.2, 5]
    )

    # =====================================================
    # FILTROS
    # =====================================================

    with col_filtros:

        st.markdown(
            '<div class="filtros-titulo">🔎 Filtros</div>',
            unsafe_allow_html=True
        )

        clientes = sorted(
            df["cliente"]
            .fillna("")
            .astype(str)
            .unique()
            .tolist()
        )

        cliente_sel = st.selectbox(
            "Cliente",
            ["Todos"] + clientes
        )

        estatuses = sorted(
            df["estatus_hoja"]
            .fillna("")
            .astype(str)
            .unique()
            .tolist()
        )

        estatus_sel = st.multiselect(
            "Estatus hoja",
            estatuses,
            default=estatuses
        )

        buscar = st.text_input(
            "Buscar hoja/TR/pedido"
        )

    # =====================================================
    # FILTRAR
    # =====================================================

    df_filtrado = df.copy()

    if cliente_sel != "Todos":

        df_filtrado = df_filtrado[
            df_filtrado["cliente"] == cliente_sel
        ]

    if estatus_sel:

        df_filtrado = df_filtrado[
            df_filtrado["estatus_hoja"]
            .isin(estatus_sel)
        ]

    if buscar.strip() != "":

        buscar_txt = buscar.lower()

        mascara = (

            df_filtrado["folio_hoja_carga"]
            .astype(str)
            .str.lower()
            .str.contains(buscar_txt, na=False)

            |

            df_filtrado["codigo_transporte"]
            .astype(str)
            .str.lower()
            .str.contains(buscar_txt, na=False)

            |

            df_filtrado["pedido"]
            .astype(str)
            .str.lower()
            .str.contains(buscar_txt, na=False)
        )

        df_filtrado = df_filtrado[
            mascara
        ]

    # =====================================================
    # KPIS
    # =====================================================

    with col_contenido:

        total_hojas = (
            df_filtrado["folio_hoja_carga"]
            .nunique()
        )

        total_pedidos = (
            df_filtrado["pedido"]
            .nunique()
        )

        total_materiales = int(
            pd.to_numeric(
                df_filtrado["total_materiales"],
                errors="coerce"
            ).fillna(0).sum()
        )

        total_piezas = int(
            pd.to_numeric(
                df_filtrado["total_piezas"],
                errors="coerce"
            ).fillna(0).sum()
        )

        total_tarimas = int(
            pd.to_numeric(
                df_filtrado["total_tarimas"],
                errors="coerce"
            ).fillna(0).sum()
        )

        total_peso = round(
            pd.to_numeric(
                df_filtrado["peso_total"],
                errors="coerce"
            ).fillna(0).sum(),
            2
        )

        k1, k2, k3, k4, k5, k6 = st.columns(6)

        with k1:
            st.metric("Hojas", total_hojas)

        with k2:
            st.metric("Pedidos", total_pedidos)

        with k3:
            st.metric("Materiales", total_materiales)

        with k4:
            st.metric("Piezas", total_piezas)

        with k5:
            st.metric("Tarimas", total_tarimas)

        with k6:
            st.metric("Peso", total_peso)

        st.divider()

        # =====================================================
        # GRID
        # =====================================================

        st.subheader(
            "📋 Hojas de carga"
        )

        columnas_grid = [

            "folio_hoja_carga",
            "estatus_visual",
            "tr_visual",
            "cliente",
            "destino",
            "pedido",
            "total_materiales",
            "total_piezas",
            "total_tarimas",
            "peso_total",
            "volumen_total",
            "fecha_creacion"
        ]

        df_grid = df_filtrado[
            columnas_grid
        ].copy()

        df_grid.insert(
            0,
            "Seleccionar",
            False
        )

        df_editado = st.data_editor(

            df_grid,

            use_container_width=True,

            hide_index=True,

            height=450,

            column_config={

                "Seleccionar": st.column_config.CheckboxColumn(
                    "Seleccionar",
                    default=False
                )

            },

            disabled=[
                col for col in df_grid.columns
                if col != "Seleccionar"
            ]
        )

        # =====================================================
        # DETALLE VISUAL
        # =====================================================

        seleccionados = df_editado[
            df_editado["Seleccionar"] == True
        ]

        if not seleccionados.empty:

            st.divider()

            st.subheader(
                "📦 Detalle hojas seleccionadas"
            )

            hojas_sel = seleccionados[
                "folio_hoja_carga"
            ].tolist()

            df_detalle = df_filtrado[
                df_filtrado["folio_hoja_carga"]
                .isin(hojas_sel)
            ]

            for _, row in df_detalle.iterrows():

                with st.container(border=True):

                    c1, c2, c3, c4 = st.columns(
                        [2, 2, 2, 2]
                    )

                    with c1:

                        st.markdown(
                            f"""
                            ### 📦 {row['folio_hoja_carga']}
                            """
                        )

                        st.write(
                            f"👤 Cliente: {row['cliente']}"
                        )

                        st.write(
                            f"📍 Destino: {row['destino']}"
                        )

                    with c2:

                        st.write(
                            f"🚛 TR: {row['tr_visual']}"
                        )

                        st.write(
                            f"📋 Pedido: {row['pedido']}"
                        )

                        st.write(
                            f"📌 Estatus: {row['estatus_visual']}"
                        )

                    with c3:

                        st.write(
                            f"📦 Materiales: {row['total_materiales']}"
                        )

                        st.write(
                            f"📦 Tarimas: {row['total_tarimas']}"
                        )

                        st.write(
                            f"📦 Piezas: {row['total_piezas']}"
                        )

                    with c4:

                        st.write(
                            f"⚖️ Peso: {row['peso_total']}"
                        )

                        st.write(
                            f"📐 Volumen: {row['volumen_total']}"
                        )

                        st.write(
                            f"👤 Usuario: {row['usuario']}"
                        )

                    if str(row["transportista"]).strip() != "":

                        st.info(
                            f"""
                            🚚 Transporte:
                            {row['transportista']}
                            | {row['vehiculo']}
                            | {row['placas']}
                            | Operador: {row['operador']}
                            """
                        )

                    if str(row["observaciones"]).strip() != "":

                        st.warning(
                            f"""
                            📝 Observaciones:
                            {row['observaciones']}
                            """
                        )

                    st.divider()


# =====================================================
# EJECUCION
# =====================================================

if __name__ == "__main__":

    consulta_hoja_carga_app()
