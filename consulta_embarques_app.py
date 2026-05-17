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
# OBTENER DETALLE POR EMBARQUES SELECCIONADOS
# =====================================================

def obtener_detalle_embarques(df_seleccionados):

    db_path = get_db_path("logistica")
    conn = sqlite3.connect(db_path)

    folios_embarque = (
        df_seleccionados["folio_embarque"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    folios_hoja_carga = (
        df_seleccionados["folio_hoja_carga"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    folios_hoja_carga = [
        x for x in folios_hoja_carga
        if x and x.lower() != "none"
    ]

    condiciones = []
    params = []

    if folios_embarque:
        marcas = ",".join(["?"] * len(folios_embarque))
        condiciones.append(f"TRIM(folio_embarque) IN ({marcas})")
        params.extend(folios_embarque)

    if folios_hoja_carga:
        marcas = ",".join(["?"] * len(folios_hoja_carga))
        condiciones.append(f"TRIM(folio_hoja_carga) IN ({marcas})")
        params.extend(folios_hoja_carga)

    if not condiciones:
        conn.close()
        return pd.DataFrame()

    query = f"""
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
        WHERE {" OR ".join(condiciones)}
        ORDER BY
            folio_embarque,
            folio_hoja_carga,
            codigo_material
    """

    df = pd.read_sql_query(
        query,
        conn,
        params=params
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
    # APLICAR FILTROS
    # =====================================================

    df_filtrado = df.copy()

    if filtro_folio != "Todos":
        df_filtrado = df_filtrado[
            df_filtrado["folio_embarque"].astype(str) == filtro_folio
        ]

    if filtro_cliente != "Todos":
        df_filtrado = df_filtrado[
            df_filtrado["cliente"].astype(str) == filtro_cliente
        ]

    if filtro_pedido != "Todos":
        df_filtrado = df_filtrado[
            df_filtrado["pedido"].astype(str) == filtro_pedido
        ]

    if filtro_estatus != "Todos":
        df_filtrado = df_filtrado[
            df_filtrado["estatus"].astype(str) == filtro_estatus
        ]

    if filtro_alerta != "Todos":
        df_filtrado = df_filtrado[
            df_filtrado["alerta"].astype(str) == filtro_alerta
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

            st.info(
                "Selecciona uno o varios embarques en la columna Sel. para revisar su detalle."
            )

            df_grid = df_filtrado.copy()
            df_grid.insert(0, "Sel.", False)

            columnas_grid = [
                "Sel.",
                "folio_embarque",
                "folio_hoja_carga",
                "folio_ruta",
                "pedido",
                "fecha",
                "cliente",
                "destino",
                "transportista",
                "vehiculo",
                "placas",
                "operador",
                "ruta",
                "estatus",
                "alerta"
            ]

            columnas_grid = [
                col for col in columnas_grid
                if col in df_grid.columns
            ]

            df_editado = st.data_editor(
                df_grid[columnas_grid],
                use_container_width=True,
                height=520,
                hide_index=True,
                disabled=[
                    col for col in columnas_grid
                    if col != "Sel."
                ],
                column_config={
                    "Sel.": st.column_config.CheckboxColumn(
                        "Sel.",
                        help="Selecciona el embarque para consultar detalle",
                        default=False
                    )
                },
                key="grid_embarques_consulta"
            )

            df_seleccionados = df_editado[
                df_editado["Sel."] == True
            ].copy()

            if not df_seleccionados.empty:

                st.session_state["embarques_seleccionados_consulta"] = (
                    df_seleccionados
                    .drop(columns=["Sel."], errors="ignore")
                    .copy()
                )

                st.success(
                    f"Embarques seleccionados: {len(df_seleccionados)}"
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

            df_seleccionados = st.session_state.get(
                "embarques_seleccionados_consulta",
                pd.DataFrame()
            )

            if df_seleccionados.empty:

                st.info(
                    "Primero selecciona uno o varios embarques en la pestaña Dashboard."
                )
                return

            st.subheader("📄 Detalle de embarques seleccionados")

            df_detalle = obtener_detalle_embarques(
                df_seleccionados
            )

            if df_detalle.empty:

                st.warning(
                    "No se encontró detalle para los embarques seleccionados."
                )
                return

            for col in [
                "cantidad_pedida",
                "cantidad_embarcar",
                "peso",
                "volumen"
            ]:
                if col in df_detalle.columns:
                    df_detalle[col] = pd.to_numeric(
                        df_detalle[col],
                        errors="coerce"
                    ).fillna(0)

            resumen = (
                df_detalle
                .groupby(
                    [
                        "folio_embarque",
                        "folio_hoja_carga"
                    ],
                    dropna=False
                )
                .agg(
                    lineas=("codigo_material", "count"),
                    cantidad_pedida=("cantidad_pedida", "sum"),
                    cantidad_embarcar=("cantidad_embarcar", "sum"),
                    peso=("peso", "sum"),
                    volumen=("volumen", "sum")
                )
                .reset_index()
            )

            st.markdown("### 📌 Resumen por embarque")

            st.dataframe(
                resumen,
                use_container_width=True,
                hide_index=True,
                height=220
            )

            st.markdown("### 📦 Cortes de detalle por embarque")

            folios_detalle = (
                df_detalle["folio_embarque"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            for folio in folios_detalle:

                df_corte = df_detalle[
                    df_detalle["folio_embarque"].astype(str) == folio
                ].copy()

                hoja = ""

                if "folio_hoja_carga" in df_corte.columns:
                    hoja = str(
                        df_corte["folio_hoja_carga"]
                        .dropna()
                        .astype(str)
                        .iloc[0]
                    )

                total_lineas = len(df_corte)
                total_pedida = df_corte["cantidad_pedida"].sum()
                total_embarcar = df_corte["cantidad_embarcar"].sum()
                total_peso = df_corte["peso"].sum()
                total_volumen = df_corte["volumen"].sum()

                with st.expander(
                    f"🚚 Embarque {folio} | Hoja carga {hoja} | Líneas {total_lineas}",
                    expanded=True
                ):

                    c1, c2, c3, c4 = st.columns(4)

                    with c1:
                        st.metric("Cantidad pedida", f"{total_pedida:,.2f}")

                    with c2:
                        st.metric("Cantidad embarcar", f"{total_embarcar:,.2f}")

                    with c3:
                        st.metric("Peso", f"{total_peso:,.2f}")

                    with c4:
                        st.metric("Volumen", f"{total_volumen:,.3f}")

                    st.dataframe(
                        df_corte,
                        use_container_width=True,
                        hide_index=True,
                        height=280
                    )

            st.markdown("### ✅ Total general seleccionado")

            tg1, tg2, tg3, tg4, tg5 = st.columns(5)

            with tg1:
                st.metric("Embarques", len(folios_detalle))

            with tg2:
                st.metric("Líneas", len(df_detalle))

            with tg3:
                st.metric(
                    "Cantidad embarcar",
                    f"{df_detalle['cantidad_embarcar'].sum():,.2f}"
                )

            with tg4:
                st.metric(
                    "Peso",
                    f"{df_detalle['peso'].sum():,.2f}"
                )

            with tg5:
                st.metric(
                    "Volumen",
                    f"{df_detalle['volumen'].sum():,.3f}"
                )

            archivo_excel_detalle = exportar_excel(
                df_detalle
            )

            st.download_button(
                label="📥 Exportar detalle seleccionado Excel",
                data=archivo_excel_detalle,
                file_name="detalle_embarques_seleccionados.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    consulta_embarques_app()
