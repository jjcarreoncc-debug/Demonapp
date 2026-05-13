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

def exportar_excel(df, nombre_archivo):

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

    st.title("🔎 Consulta embarques")

    # =====================================================
    # CONSULTA
    # =====================================================

    try:

        df = obtener_embarques()

    except Exception as e:

        st.error("❌ Error consultando embarques")
        st.exception(e)

        return

    if df.empty:

        st.warning("No existen embarques registrados.")

        return

    # =====================================================
    # FILTROS
    # =====================================================

    st.subheader("📋 Filtros")

    col1, col2, col3 = st.columns(3)

    with col1:

        filtro_folio = st.text_input(
            "Folio embarque"
        )

        filtro_pedido = st.text_input(
            "Pedido"
        )

    with col2:

        filtro_cliente = st.text_input(
            "Cliente"
        )

        filtro_estatus = st.selectbox(
            "Estatus",
            ["Todos"] + sorted(df["estatus"].dropna().unique().tolist())
        )

    with col3:

        fecha_inicio = st.date_input(
            "Fecha inicio",
            value=None
        )

        fecha_fin = st.date_input(
            "Fecha fin",
            value=None
        )

    # =====================================================
    # FILTROS DF
    # =====================================================

    df_filtrado = df.copy()

    if filtro_folio:

        df_filtrado = df_filtrado[
            df_filtrado["folio_embarque"]
            .astype(str)
            .str.contains(filtro_folio, case=False, na=False)
        ]

    if filtro_pedido:

        df_filtrado = df_filtrado[
            df_filtrado["pedido"]
            .astype(str)
            .str.contains(filtro_pedido, case=False, na=False)
        ]

    if filtro_cliente:

        df_filtrado = df_filtrado[
            df_filtrado["cliente"]
            .astype(str)
            .str.contains(filtro_cliente, case=False, na=False)
        ]

    if filtro_estatus != "Todos":

        df_filtrado = df_filtrado[
            df_filtrado["estatus"] == filtro_estatus
        ]

    if fecha_inicio:

        df_filtrado = df_filtrado[
            pd.to_datetime(df_filtrado["fecha"]).dt.date >= fecha_inicio
        ]

    if fecha_fin:

        df_filtrado = df_filtrado[
            pd.to_datetime(df_filtrado["fecha"]).dt.date <= fecha_fin
        ]

    # =====================================================
    # RESULTADOS
    # =====================================================

    st.subheader("📦 Embarques")

    st.write(f"Total registros: {len(df_filtrado)}")

    st.dataframe(
        df_filtrado,
        use_container_width=True,
        height=400
    )

    # =====================================================
    # EXPORTAR
    # =====================================================

    archivo_excel = exportar_excel(
        df_filtrado,
        "consulta_embarques.xlsx"
    )

    st.download_button(
        label="📥 Exportar consulta a Excel",
        data=archivo_excel,
        file_name="consulta_embarques.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # =====================================================
    # DETALLE
    # =====================================================

    st.subheader("📄 Detalle embarque")

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

        try:

            df_detalle = obtener_detalle_embarque(
                folio_detalle
            )

            st.dataframe(
                df_detalle,
                use_container_width=True,
                height=300
            )

            archivo_detalle = exportar_excel(
                df_detalle,
                f"detalle_{folio_detalle}.xlsx"
            )

            st.download_button(
                label="📥 Exportar detalle Excel",
                data=archivo_detalle,
                file_name=f"detalle_{folio_detalle}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:

            st.error("❌ Error consultando detalle")
            st.exception(e)
