import streamlit as st
import pandas as pd
import sqlite3
import io

from sigem_db import get_db_path


# =====================================================
# OBTENER EMBARQUES
# =====================================================

def obtener_embarques():

    db_path = get_db_path("logistica")

    conn = sqlite3.connect(db_path)

    query = """
        SELECT
            folio_embarque,
            folio_hoja_carga,
            folio_ruta,
            pedido,
            fecha,
            cliente,
            destino,
            transportista,
            vehiculo,
            placas,
            operador,
            ruta,
            estatus,
            observaciones,
            usuario,
            fecha_creacion
        FROM embarques
        ORDER BY fecha DESC, folio_embarque DESC
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


# =====================================================
# OBTENER DETALLE EMBARQUE
# =====================================================

def obtener_detalle_embarque(folio_embarque):

    db_path = get_db_path("logistica")

    conn = sqlite3.connect(db_path)

    query = """
        SELECT
            d.folio_embarque,
            d.folio_hoja_carga,
            d.folio_ruta,
            d.pedido,
            d.codigo_material,
            d.descripcion,
            d.cantidad_pedida,
            d.cantidad_embarcar,
            d.peso,
            d.volumen,
            d.bodega,
            d.ubicacion
        FROM detalle_embarque d
        LEFT JOIN embarques e
            ON TRIM(e.folio_embarque) = TRIM(?)
        WHERE
            TRIM(d.folio_embarque) = TRIM(?)
            OR TRIM(d.folio_hoja_carga) = TRIM(e.folio_hoja_carga)
            OR TRIM(d.folio_ruta) = TRIM(e.folio_ruta)
            OR TRIM(d.pedido) = TRIM(e.pedido)
    """

    df = pd.read_sql_query(
        query,
        conn,
        params=[
            folio_embarque,
            folio_embarque
        ]
    )

    conn.close()

    return df
# =====================================================
# EXPORTAR EXCEL
# =====================================================

def exportar_excel(df):

    output = io.BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name="Consulta"
        )

    return output.getvalue()


# =====================================================
# ESTILOS
# =====================================================

def aplicar_estilos():

    st.markdown(
        """
        <style>

        .block-container{
            padding-top: 1rem;
            padding-bottom: 1rem;
            padding-left: 2rem;
            padding-right: 2rem;
            max-width: 100%;
        }

        .titulo-sigem{
            font-size: 38px;
            font-weight: 800;
            color: #1F4E79;
            margin-bottom: 0px;
        }

        .subtitulo-sigem{
            font-size: 15px;
            color: #5b6575;
            margin-bottom: 24px;
        }

        .filtros-titulo{
            font-size: 28px;
            font-weight: 800;
            color: #1F2937;
            margin-bottom: 20px;
        }

        div[data-testid="metric-container"]{
            background: #F8FAFC;
            border: 1px solid #DBEAFE;
            padding: 18px;
            border-radius: 16px;
            box-shadow: 0px 2px 8px rgba(0,0,0,0.04);
        }

        div[data-testid="metric-container"] label{
            font-size: 13px;
            font-weight: 600;
            color: #374151;
        }

        div[data-testid="metric-container"] [data-testid="stMetricValue"]{
            font-size: 34px;
            font-weight: 700;
            color: #111827;
        }

        .stTabs [data-baseweb="tab-list"]{
            gap: 10px;
            border-bottom: 1px solid #E5E7EB;
        }

        .stTabs [data-baseweb="tab"]{
            height: 44px;
            border-radius: 10px 10px 0px 0px;
            padding-left: 18px;
            padding-right: 18px;
            font-weight: 600;
        }

        .stDataFrame{
            border-radius: 14px;
            overflow: hidden;
            border: 1px solid #E5E7EB;
        }

        .stSelectbox label{
            font-weight: 600;
            color: #374151;
        }

        .stTextInput label{
            font-weight: 600;
            color: #374151;
        }

        </style>
        """,
        unsafe_allow_html=True
    )


# =====================================================
# APP
# =====================================================

def consulta_embarques_app():

    aplicar_estilos()

    st.markdown(
        """
        <div class="titulo-sigem">🚚 Consulta embarques</div>
        <div class="subtitulo-sigem">
            Consulta folios de embarque, revisa detalle operativo y da seguimiento al estatus logístico.
        </div>
        """,
        unsafe_allow_html=True
    )

    try:

        df = obtener_embarques()

    except Exception as e:

        st.error("❌ Error consultando embarques")
        st.exception(e)
        return

    if df.empty:

        st.warning("No existen embarques registrados.")
        return

    df["fecha"] = pd.to_datetime(
        df["fecha"],
        errors="coerce"
    )

    hoy = pd.Timestamp.today().normalize()

    df["dias_embarque"] = (
        hoy - df["fecha"]
    ).dt.days

    def calcular_alerta(row):

        dias = row["dias_embarque"]

        estatus = str(
            row.get("estatus", "")
        ).lower()

        if "entregado" in estatus:

            return "✅ Entregado"

        elif dias <= 1:

            return "🟢 Reciente"

        elif dias <= 3:

            return "🟡 En proceso"

        else:

            return "🔴 Pendiente viejo"

    df["alerta"] = df.apply(
        calcular_alerta,
        axis=1
    )

    st.divider()

    # =====================================================
    # LAYOUT PRINCIPAL
    # =====================================================

    col_filtros, col_contenido = st.columns([1, 5.5])

    # =====================================================
    # FILTROS
    # =====================================================

    with col_filtros:

        st.markdown(
            '<div class="filtros-titulo">🔎 Filtros</div>',
            unsafe_allow_html=True
        )

        folios = ["Todos"] + sorted(
            df["folio_embarque"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        clientes = ["Todos"] + sorted(
            df["cliente"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        pedidos = ["Todos"] + sorted(
            df["pedido"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        estatus_lista = ["Todos"] + sorted(
            df["estatus"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        alertas = ["Todos"] + sorted(
            df["alerta"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        filtro_folio = st.selectbox(
            "Folio embarque",
            folios
        )

        filtro_cliente = st.selectbox(
            "Cliente",
            clientes
        )

        filtro_pedido = st.selectbox(
            "Pedido",
            pedidos
        )

        filtro_estatus = st.selectbox(
            "Estatus",
            estatus_lista
        )

        filtro_alerta = st.selectbox(
            "Alerta",
            alertas
        )

        buscar = st.text_input(
            "Buscar"
        )

    # =====================================================
    # FILTROS DATAFRAME
    # =====================================================

    df_filtrado = df.copy()

    if filtro_folio != "Todos":

        df_filtrado = df_filtrado[
            df_filtrado["folio_embarque"].astype(str)
            == filtro_folio
        ]

    if filtro_cliente != "Todos":

        df_filtrado = df_filtrado[
            df_filtrado["cliente"].astype(str)
            == filtro_cliente
        ]

    if filtro_pedido != "Todos":

        df_filtrado = df_filtrado[
            df_filtrado["pedido"].astype(str)
            == filtro_pedido
        ]

    if filtro_estatus != "Todos":

        df_filtrado = df_filtrado[
            df_filtrado["estatus"].astype(str)
            == filtro_estatus
        ]

    if filtro_alerta != "Todos":

        df_filtrado = df_filtrado[
            df_filtrado["alerta"].astype(str)
            == filtro_alerta
        ]

    if buscar:

        texto_buscar = buscar.lower().strip()

        df_filtrado = df_filtrado[
            df_filtrado.astype(str)
            .apply(
                lambda fila: fila.str.lower().str.contains(
                    texto_buscar,
                    na=False
                ).any(),
                axis=1
            )
        ]

    # =====================================================
    # CONTENIDO
    # =====================================================

    with col_contenido:

        total_embarques = len(df_filtrado)

        entregados = df_filtrado[
            df_filtrado["estatus"]
            .astype(str)
            .str.lower()
            .str.contains("entregado", na=False)
        ].shape[0]

        pendientes = total_embarques - entregados

        total_pedidos = df_filtrado["pedido"].nunique()

        total_clientes = df_filtrado["cliente"].nunique()

        total_rutas = df_filtrado["folio_ruta"].nunique()

        k1, k2, k3, k4, k5, k6 = st.columns(6)

        with k1:
            st.metric("Embarques", total_embarques)

        with k2:
            st.metric("Entregados", entregados)

        with k3:
            st.metric("Pendientes", pendientes)

        with k4:
            st.metric("Pedidos", total_pedidos)

        with k5:
            st.metric("Clientes", total_clientes)

        with k6:
            st.metric("Rutas", total_rutas)

        st.divider()

        # =====================================================
        # TABS
        # =====================================================

        tab1, tab2 = st.tabs(
            [
                "📊 Dashboard",
                "📄 Detalle"
            ]
        )

        # =====================================================
        # TAB DASHBOARD
        # =====================================================

        with tab1:

            st.dataframe(
                df_filtrado,
                use_container_width=True,
                height=520,
                hide_index=True
            )

            archivo_excel = exportar_excel(
                df_filtrado
            )

            st.download_button(
                label="📥 Exportar consulta Excel",
                data=archivo_excel,
                file_name="consulta_embarques.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        # =====================================================
        # TAB DETALLE
        # =====================================================

        with tab2:

            lista_embarques = (
                df_filtrado["folio_embarque"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            if lista_embarques:

                folio_detalle = st.selectbox(
                    "Selecciona embarque",
                    lista_embarques
                )

                df_detalle = obtener_detalle_embarque(
                    folio_detalle
                )

                st.dataframe(
                    df_detalle,
                    use_container_width=True,
                    height=430,
                    hide_index=True
                )

                archivo_excel = exportar_excel(
                    df_detalle
                )

                st.download_button(
                    label="📥 Exportar detalle Excel",
                    data=archivo_excel,
                    file_name=f"detalle_{folio_detalle}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            else:

                st.info(
                    "No hay embarques para mostrar detalle."
                )


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    consulta_embarques_app()
