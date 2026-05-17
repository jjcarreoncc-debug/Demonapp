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
# OBTENER DETALLE
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

    condiciones = []
    params = []

    if folios_embarque:

        marcas = ",".join(["?"] * len(folios_embarque))

        condiciones.append(
            f"TRIM(folio_embarque) IN ({marcas})"
        )

        params.extend(folios_embarque)

    if folios_hoja_carga:

        marcas = ",".join(["?"] * len(folios_hoja_carga))

        condiciones.append(
            f"TRIM(folio_hoja_carga) IN ({marcas})"
        )

        params.extend(folios_hoja_carga)

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

        .stTabs [data-baseweb="tab-list"]{
            gap: 10px;
        }

        .stDataFrame{
            border-radius: 14px;
            overflow: hidden;
            border: 1px solid #E5E7EB;
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

        filtro_folio = st.selectbox(
            "Folio embarque",
            ["Todos"] + sorted(
                df["folio_embarque"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )
        )

        filtro_cliente = st.selectbox(
            "Cliente",
            ["Todos"] + sorted(
                df["cliente"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )
        )

        filtro_pedido = st.selectbox(
            "Pedido",
            ["Todos"] + sorted(
                df["pedido"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )
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

        buscar = st.text_input(
            "Buscar"
        )

    # =====================================================
    # APLICAR FILTROS
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

    if buscar:

        texto = buscar.lower().strip()

        df_filtrado = df_filtrado[
            df_filtrado.astype(str)
            .apply(
                lambda fila: fila.str.lower().str.contains(
                    texto,
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

        total_clientes = df_filtrado["cliente"].nunique()
        total_rutas = df_filtrado["folio_ruta"].nunique()
        total_pedidos = df_filtrado["pedido"].nunique()

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
        # DASHBOARD
        # =====================================================
        with tab1:

            st.markdown("### 📦 Selección de embarques")
        
            opciones_embarque = (
                df_filtrado["folio_embarque"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )
        
            embarques_seleccionados = st.multiselect(
                "Selecciona uno o varios embarques",
                opciones_embarque,
                placeholder="Selecciona embarques..."
            )
        
            if embarques_seleccionados:
        
                st.success(
                    f"Embarques seleccionados: {len(embarques_seleccionados)}"
                )
        
            st.dataframe(
                df_filtrado,
                use_container_width=True,
                height=500,
                hide_index=True
            )
                    ########
            
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
        # DETALLE
        # =====================================================

        with tab2:

            if not embarques_seleccionados:

                st.info(
                    "Selecciona uno o varios embarques en Dashboard."
                )

                return

            df_seleccionados = df_filtrado[
                df_filtrado["folio_embarque"]
                .astype(str)
                .isin(embarques_seleccionados)
            ].copy()

            df_detalle = obtener_detalle_embarques(
                df_seleccionados
            )

            if df_detalle.empty:

                st.warning(
                    "No se encontró detalle."
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
                    ]
                )
                .agg(
                    lineas=("codigo_material", "count"),
                    cantidad_embarcar=("cantidad_embarcar", "sum"),
                    peso=("peso", "sum"),
                    volumen=("volumen", "sum")
                )
                .reset_index()
            )

            st.markdown("### 📌 Resumen")

            st.dataframe(
                resumen,
                use_container_width=True,
                hide_index=True,
                height=220
            )

            st.markdown("### 📦 Detalle por embarque")

            for folio in embarques_seleccionados:

                df_corte = df_detalle[
                    df_detalle["folio_embarque"]
                    .astype(str)
                    == str(folio)
                ].copy()

                if df_corte.empty:
                    continue

                hoja = str(
                    df_corte["folio_hoja_carga"]
                    .iloc[0]
                )

                total_lineas = len(df_corte)

                with st.expander(
                    f"🚚 {folio} | Hoja carga {hoja} | Líneas {total_lineas}",
                    expanded=True
                ):

                    c1, c2, c3, c4 = st.columns(4)

                    with c1:
                        st.metric(
                            "Cantidad embarcar",
                            f"{df_corte['cantidad_embarcar'].sum():,.2f}"
                        )

                    with c2:
                        st.metric(
                            "Peso",
                            f"{df_corte['peso'].sum():,.2f}"
                        )

                    with c3:
                        st.metric(
                            "Volumen",
                            f"{df_corte['volumen'].sum():,.3f}"
                        )

                    with c4:
                        st.metric(
                            "Líneas",
                            total_lineas
                        )

                    st.dataframe(
                        df_corte,
                        use_container_width=True,
                        hide_index=True,
                        height=300
                    )

            archivo_excel_detalle = exportar_excel(
                df_detalle
            )

            st.download_button(
                label="📥 Exportar detalle Excel",
                data=archivo_excel_detalle,
                file_name="detalle_embarques.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    consulta_embarques_app()
