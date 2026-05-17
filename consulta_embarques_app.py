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
            folio_embarque,
            folio_hoja_carga,
            folio_ruta,
            pedido,
            codigo_material,
            descripcion,
            cantidad_pedida,
            cantidad_embarcar,
            peso,
            volumen,
            bodega,
            ubicacion
        FROM detalle_embarque
        WHERE folio_embarque = ?
    """

    df = pd.read_sql_query(
        query,
        conn,
        params=[folio_embarque]
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
# APP
# =====================================================

def consulta_embarques_app():

    st.markdown(
        """
        <style>
        .titulo-sigem {
            font-size: 34px;
            font-weight: 800;
            color: #1f4e79;
            margin-bottom: 4px;
        }

        .subtitulo-sigem {
            font-size: 15px;
            color: #555;
            margin-bottom: 28px;
        }

        .bloque-filtros {
            font-size: 26px;
            font-weight: 800;
            color: #1f2937;
            margin-bottom: 16px;
        }

        div[data-testid="metric-container"] {
            background-color: #f8fafc;
            border: 1px solid #dbeafe;
            padding: 18px;
            border-radius: 14px;
            box-shadow: 0px 2px 8px rgba(0,0,0,0.04);
        }

        div[data-testid="metric-container"] label {
            font-size: 13px;
            color: #1f2937;
        }

        div[data-testid="metric-container"] [data-testid="stMetricValue"] {
            font-size: 30px;
            color: #111827;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

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

    col_filtros, col_contenido = st.columns([1.1, 5])

    with col_filtros:

        st.markdown(
            '<div class="bloque-filtros">🔎 Filtros</div>',
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

        tab1, tab2 = st.tabs(
            [
                "📊 Dashboard",
                "📄 Detalle"
            ]
        )

        with tab1:

            st.dataframe(
                df_filtrado,
                use_container_width=True,
                height=500,
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
                    height=400,
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

                st.info("No hay embarques para mostrar detalle.")


if __name__ == "__main__":

    consulta_embarques_app()
