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

    st.title("🚚 Consulta embarques")

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

    col_filtros, col_contenido = st.columns([1.05, 5])

    with col_filtros:

        st.subheader("🔎 Filtros")

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

    with col_contenido:

        total_embarques = len(df_filtrado)

        entregados = df_filtrado[
            df_filtrado["estatus"]
            .astype(str)
            .str.lower()
            .str.contains("entregado", na=False)
        ].shape[0]

        pendientes = total_embarques - entregados

        k1, k2, k3 = st.columns(3)

        with k1:
            st.metric("Embarques", total_embarques)

        with k2:
            st.metric("Entregados", entregados)

        with k3:
            st.metric("Pendientes", pendientes)

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


if __name__ == "__main__":

    consulta_embarques_app()
