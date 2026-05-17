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

    # =====================================================
    # FILTROS IZQUIERDA
    # =====================================================

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

    # =====================================================
    # FILTRADO
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

    if buscar.strip():

        texto = buscar.strip().lower()

        df_filtrado = df_filtrado[
            df_filtrado["folio_embarque"].astype(str).str.lower().str.contains(texto, na=False)
            | df_filtrado["folio_hoja_carga"].astype(str).str.lower().str.contains(texto, na=False)
            | df_filtrado["pedido"].astype(str).str.lower().str.contains(texto, na=False)
            | df_filtrado["cliente"].astype(str).str.lower().str.contains(texto, na=False)
            | df_filtrado["destino"].astype(str).str.lower().str.contains(texto, na=False)
            | df_filtrado["transportista"].astype(str).str.lower().str.contains(texto, na=False)
            | df_filtrado["vehiculo"].astype(str).str.lower().str.contains(texto, na=False)
            | df_filtrado["placas"].astype(str).str.lower().str.contains(texto, na=False)
            | df_filtrado["operador"].astype(str).str.lower().str.contains(texto, na=False)
        ]

    # =====================================================
    # CONTENIDO DERECHA
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

        pendientes_viejos = df_filtrado[
            df_filtrado["alerta"] == "🔴 Pendiente viejo"
        ].shape[0]

        clientes_total = df_filtrado["cliente"].nunique()

        rutas = df_filtrado["ruta"].nunique()

        k1, k2, k3, k4, k5, k6 = st.columns(6)

        with k1:
            st.metric("Embarques", total_embarques)

        with k2:
            st.metric("Entregados", entregados)

        with k3:
            st.metric("Pendientes", pendientes)

        with k4:
            st.metric("Viejos", pendientes_viejos)

        with k5:
            st.metric("Clientes", clientes_total)

        with k6:
            st.metric("Rutas", rutas)

        st.divider()

        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
            [
                "📊 Dashboard",
                "🚦 Alertas",
                "📦 Pendientes",
                "🚚 En tránsito",
                "✅ Entregados",
                "📄 Detalle"
            ]
        )

        # =====================================================
        # DASHBOARD
        # =====================================================

        with tab1:

            columnas_dashboard = [
                "alerta",
                "estatus",
                "folio_embarque",
                "folio_hoja_carga",
                "fecha",
                "cliente",
                "destino",
                "transportista",
                "vehiculo",
                "placas"
            ]

            columnas_dashboard = [
                col for col in columnas_dashboard
                if col in df_filtrado.columns
            ]

            st.subheader("📦 Base general de embarques")

            st.dataframe(
                df_filtrado[columnas_dashboard],
                use_container_width=True,
                height=430,
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

            columnas_alertas = [
                "alerta",
                "estatus",
                "folio_embarque",
                "fecha",
                "cliente",
                "destino",
                "transportista",
                "vehiculo",
                "placas",
                "dias_embarque"
            ]

            columnas_alertas = [
                col for col in columnas_alertas
                if col in df_alertas.columns
            ]

            st.dataframe(
                df_alertas[columnas_alertas],
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

            columnas_pendientes = [
                "alerta",
                "estatus",
                "folio_embarque",
                "fecha",
                "cliente",
                "destino",
                "transportista",
                "vehiculo",
                "placas"
            ]

            columnas_pendientes = [
                col for col in columnas_pendientes
                if col in df_pendientes.columns
            ]

            st.dataframe(
                df_pendientes[columnas_pendientes],
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
                .str.contains("transito|tránsito", na=False)
            ]

            st.subheader("🚚 Embarques en tránsito")

            columnas_transito = [
                "alerta",
                "estatus",
                "folio_embarque",
                "fecha",
                "cliente",
                "destino",
                "transportista",
                "vehiculo",
                "placas"
            ]

            columnas_transito = [
                col for col in columnas_transito
                if col in df_transito.columns
            ]

            st.dataframe(
                df_transito[columnas_transito],
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

            columnas_entregados = [
                "alerta",
                "estatus",
                "folio_embarque",
                "fecha",
                "cliente",
                "destino",
                "transportista",
                "vehiculo",
                "placas"
            ]

            columnas_entregados = [
                col for col in columnas_entregados
                if col in df_entregados.columns
            ]

            st.dataframe(
                df_entregados[columnas_entregados],
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

            if not lista_embarques:

                st.info(
                    "No hay embarques para mostrar detalle."
                )

                return

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
                        f"**Placas:** {embarque['placas
