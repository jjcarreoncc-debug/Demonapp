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
    # FECHAS
    # =====================================================

    df["fecha"] = pd.to_datetime(
        df["fecha"],
        errors="coerce"
    )

    hoy = pd.Timestamp.today().normalize()

    df["dias_embarque"] = (
        hoy - df["fecha"]
    ).dt.days

    # =====================================================
    # ALERTAS
    # =====================================================

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

    # =====================================================
    # FILTROS
    # =====================================================

    st.subheader("🔎 Filtros")

    col1, col2, col3 = st.columns(3)

    with col1:

        filtro_folio = st.text_input(
            "Folio embarque"
        )

        filtro_cliente = st.text_input(
            "Cliente"
        )

    with col2:

        filtro_pedido = st.text_input(
            "Pedido"
        )

        filtro_estatus = st.selectbox(
            "Estatus",
            ["Todos"] + sorted(
                df["estatus"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )
        )

    with col3:

        filtro_alerta = st.selectbox(
            "Alerta",
            ["Todos"] + sorted(
                df["alerta"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )
        )

    # =====================================================
    # FILTRADO
    # =====================================================

    df_filtrado = df.copy()

    if filtro_folio:

        df_filtrado = df_filtrado[
            df_filtrado["folio_embarque"]
            .astype(str)
            .str.contains(
                filtro_folio,
                case=False,
                na=False
            )
        ]

    if filtro_cliente:

        df_filtrado = df_filtrado[
            df_filtrado["cliente"]
            .astype(str)
            .str.contains(
                filtro_cliente,
                case=False,
                na=False
            )
        ]

    if filtro_pedido:

        df_filtrado = df_filtrado[
            df_filtrado["pedido"]
            .astype(str)
            .str.contains(
                filtro_pedido,
                case=False,
                na=False
            )
        ]

    if filtro_estatus != "Todos":

        df_filtrado = df_filtrado[
            df_filtrado["estatus"] == filtro_estatus
        ]

    if filtro_alerta != "Todos":

        df_filtrado = df_filtrado[
            df_filtrado["alerta"] == filtro_alerta
        ]

    # =====================================================
    # TABS
    # =====================================================

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([

        "Dashboard",
        "Alertas",
        "Pendientes",
        "En tránsito",
        "Entregados",
        "Detalle"

    ])

    # =====================================================
    # DASHBOARD
    # =====================================================

    with tab1:

        total_embarques = len(df_filtrado)

        entregados = df_filtrado[
            df_filtrado["estatus"]
            .astype(str)
            .str.lower()
            .str.contains("entregado", na=False)
        ].shape[0]

        pendientes = total_embarques - entregados

        pendientes_viejos = df_filtrado[
            df_filtrado["alerta"] == "🔴 Pendiente viejo"
        ].shape[0]

        clientes = df_filtrado["cliente"].nunique()

        rutas = df_filtrado["ruta"].nunique()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("📦 Embarques", total_embarques)

        with col2:
            st.metric("✅ Entregados", entregados)

        with col3:
            st.metric("⏳ Pendientes", pendientes)

        col4, col5, col6 = st.columns(3)

        with col4:
            st.metric("🔴 Pendientes viejos", pendientes_viejos)

        with col5:
            st.metric("👥 Clientes", clientes)

        with col6:
            st.metric("🛣️ Rutas", rutas)

        st.divider()

        columnas_dashboard = [

            "folio_embarque",
            "folio_hoja_carga",
            "fecha",
            "cliente",
            "destino",
            "transportista",
            "estatus",
            "alerta"

        ]

        st.dataframe(
            df_filtrado[columnas_dashboard],
            use_container_width=True,
            height=400,
            hide_index=True
        )

    # =====================================================
    # ALERTAS
    # =====================================================

    with tab2:

        df_alertas = df_filtrado[
            df_filtrado["alerta"] != "✅ Entregado"
        ]

        st.subheader("🚦 Embarques con alertas")

        st.dataframe(
            df_alertas,
            use_container_width=True,
            height=500,
            hide_index=True
        )

    # =====================================================
    # PENDIENTES
    # =====================================================

    with tab3:

        df_pendientes = df_filtrado[
            ~df_filtrado["estatus"]
            .astype(str)
            .str.lower()
            .str.contains("entregado", na=False)
        ]

        st.subheader("📦 Embarques pendientes")

        st.dataframe(
            df_pendientes,
            use_container_width=True,
            height=500,
            hide_index=True
        )

    # =====================================================
    # EN TRANSITO
    # =====================================================

    with tab4:

        df_transito = df_filtrado[
            df_filtrado["estatus"]
            .astype(str)
            .str.lower()
            .str.contains("transito", na=False)
        ]

        st.subheader("🚚 Embarques en tránsito")

        st.dataframe(
            df_transito,
            use_container_width=True,
            height=500,
            hide_index=True
        )

    # =====================================================
    # ENTREGADOS
    # =====================================================

    with tab5:

        df_entregados = df_filtrado[
            df_filtrado["estatus"]
            .astype(str)
            .str.lower()
            .str.contains("entregado", na=False)
        ]

        st.subheader("✅ Embarques entregados")

        st.dataframe(
            df_entregados,
            use_container_width=True,
            height=500,
            hide_index=True
        )

    # =====================================================
    # DETALLE
    # =====================================================

    with tab6:

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

                embarque = df_filtrado[
                    df_filtrado["folio_embarque"]
                    == folio_detalle
                ].iloc[0]

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.write(
                        f"**Folio:** {embarque['folio_embarque']}"
                    )

                    st.write(
                        f"**Hoja carga:** {embarque['folio_hoja_carga']}"
                    )

                    st.write(
                        f"**Ruta:** {embarque['folio_ruta']}"
                    )

                with col2:

                    st.write(
                        f"**Cliente:** {embarque['cliente']}"
                    )

                    st.write(
                        f"**Destino:** {embarque['destino']}"
                    )

                    st.write(
                        f"**Transportista:** {embarque['transportista']}"
                    )

                with col3:

                    st.write(
                        f"**Vehículo:** {embarque['vehiculo']}"
                    )

                    st.write(
                        f"**Placas:** {embarque['placas']}"
                    )

                    st.write(
                        f"**Estatus:** {embarque['estatus']}"
                    )

                st.divider()

                df_detalle = obtener_detalle_embarque(
                    folio_detalle
                )

                st.dataframe(
                    df_detalle,
                    use_container_width=True,
                    height=350,
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

            except Exception as e:

                st.error("❌ Error consultando detalle")
                st.exception(e)
