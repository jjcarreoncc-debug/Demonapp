import streamlit as st
import pandas as pd
import sqlite3

from sigem_db import get_db_path


def obtener_kardex():

    db_path = get_db_path("inventarios")
    conn = sqlite3.connect(db_path)

    query = """
        SELECT
            id_movimiento,
            folio_movimiento,
            fecha,
            tipo_movimiento,
            tipo_documento,
            numero_documento,
            codigo_material,
            descripcion,
            cantidad,
            bodega,
            ubicacion,
            referencia,
            comentarios,
            usuario
        FROM movimientos_inventario
        ORDER BY fecha DESC, id_movimiento DESC
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    return df


def normalizar_tipo_movimiento(valor):

    texto = str(valor).strip().upper()

    if texto.startswith("ENTRADA"):
        return "ENTRADA"

    if texto.startswith("SALIDA"):
        return "SALIDA"

    if texto == "RESERVA":
        return "RESERVA"

    if "AJUSTE" in texto:
        return "AJUSTE"

    if "TRANSFERENCIA" in texto:
        return "TRANSFERENCIA"

    return texto if texto else "SIN TIPO"


def preparar_kardex(df):

    df["fecha"] = pd.to_datetime(
        df["fecha"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["fecha"]
    ).copy()

    df["tipo_movimiento_norm"] = df["tipo_movimiento"].apply(
        normalizar_tipo_movimiento
    )

    df["cantidad"] = pd.to_numeric(
        df["cantidad"],
        errors="coerce"
    ).fillna(0)

    df["entrada"] = df.apply(
        lambda row: row["cantidad"]
        if row["tipo_movimiento_norm"] == "ENTRADA"
        else 0,
        axis=1
    )

    df["salida"] = df.apply(
        lambda row: abs(row["cantidad"])
        if row["tipo_movimiento_norm"] == "SALIDA"
        else 0,
        axis=1
    )

    df["reserva"] = df.apply(
        lambda row: row["cantidad"]
        if row["tipo_movimiento_norm"] == "RESERVA"
        else 0,
        axis=1
    )

    df["ajuste"] = df.apply(
        lambda row: row["cantidad"]
        if row["tipo_movimiento_norm"] == "AJUSTE"
        else 0,
        axis=1
    )

    df["impacto_stock"] = (
        df["entrada"]
        -
        df["salida"]
        +
        df["ajuste"]
    )

    df = df.sort_values(
        by=[
            "codigo_material",
            "bodega",
            "fecha",
            "id_movimiento"
        ]
    )

    df["saldo_material_bodega"] = df.groupby(
        [
            "codigo_material",
            "bodega"
        ]
    )["impacto_stock"].cumsum()

    return df


def aplicar_filtros_laterales(df):

    st.subheader("🔎 Filtros rápidos")

    fecha_min = df["fecha"].min().date()
    fecha_max = df["fecha"].max().date()

    rango_fechas = st.date_input(
        "Fecha",
        value=(fecha_min, fecha_max)
    )

    bodegas = ["Todas"] + sorted(
        df["bodega"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    bodega = st.selectbox(
        "Bodega",
        bodegas
    )

    materiales = ["Todos"] + sorted(
        (
            df["codigo_material"].astype(str)
            + " - "
            + df["descripcion"].astype(str)
        )
        .dropna()
        .unique()
        .tolist()
    )

    material_combo = st.selectbox(
        "Material",
        materiales
    )

    tipos = ["Todos"] + sorted(
        df["tipo_movimiento_norm"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    tipo = st.selectbox(
        "Tipo movimiento",
        tipos
    )

    documentos = ["Todos"] + sorted(
        df["tipo_documento"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    documento = st.selectbox(
        "Tipo documento",
        documentos
    )

    texto_busqueda = st.text_input(
        "Folio / documento / referencia",
        placeholder="Buscar folio..."
    )

    df_filtrado = df.copy()

    if isinstance(rango_fechas, tuple) and len(rango_fechas) == 2:

        fecha_inicio, fecha_fin = rango_fechas

        df_filtrado = df_filtrado[
            (df_filtrado["fecha"].dt.date >= fecha_inicio)
            &
            (df_filtrado["fecha"].dt.date <= fecha_fin)
        ]

    if bodega != "Todas":

        df_filtrado = df_filtrado[
            df_filtrado["bodega"].astype(str) == bodega
        ]

    if material_combo != "Todos":

        codigo_material = material_combo.split(" - ")[0].strip()

        df_filtrado = df_filtrado[
            df_filtrado["codigo_material"].astype(str) == codigo_material
        ]

    if tipo != "Todos":

        df_filtrado = df_filtrado[
            df_filtrado["tipo_movimiento_norm"].astype(str) == tipo
        ]

    if documento != "Todos":

        df_filtrado = df_filtrado[
            df_filtrado["tipo_documento"].astype(str) == documento
        ]

    if texto_busqueda.strip():

        texto = texto_busqueda.strip().lower()

        df_filtrado = df_filtrado[
            df_filtrado["folio_movimiento"].astype(str).str.lower().str.contains(texto, na=False)
            |
            df_filtrado["numero_documento"].astype(str).str.lower().str.contains(texto, na=False)
            |
            df_filtrado["referencia"].astype(str).str.lower().str.contains(texto, na=False)
            |
            df_filtrado["comentarios"].astype(str).str.lower().str.contains(texto, na=False)
        ]

    st.divider()

    st.subheader("📌 Vistas rápidas")

    if st.button(
        "Movimientos recientes",
        use_container_width=True
    ):

        fecha_corte = df["fecha"].max() - pd.Timedelta(days=30)

        df_filtrado = df[
            df["fecha"] >= fecha_corte
        ].copy()

    if st.button(
        "Solo entradas",
        use_container_width=True
    ):

        df_filtrado = df[
            df["tipo_movimiento_norm"] == "ENTRADA"
        ].copy()

    if st.button(
        "Solo salidas",
        use_container_width=True
    ):

        df_filtrado = df[
            df["tipo_movimiento_norm"] == "SALIDA"
        ].copy()

    if st.button(
        "Solo reservas",
        use_container_width=True
    ):

        df_filtrado = df[
            df["tipo_movimiento_norm"] == "RESERVA"
        ].copy()

    return df_filtrado


def mostrar_kpis_superiores(df):

    entradas = df["entrada"].sum()
    salidas = df["salida"].sum()
    reservas = df["reserva"].sum()
    saldo = df["impacto_stock"].sum()
    disponible = saldo - reservas
    movimientos = len(df)

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        st.metric(
            "Inventario actual",
            f"{saldo:,.2f}",
            "pzas"
        )

    with c2:
        st.metric(
            "Entradas",
            f"{entradas:,.2f}",
            "pzas"
        )

    with c3:
        st.metric(
            "Salidas",
            f"{salidas:,.2f}",
            "pzas"
        )

    with c4:
        st.metric(
            "Reservas",
            f"{reservas:,.2f}",
            "pzas"
        )

    with c5:
        st.metric(
            "Disponible",
            f"{disponible:,.2f}",
            "pzas"
        )

    with c6:
        st.metric(
            "Movimientos",
            f"{movimientos:,.0f}",
            "registros"
        )


def mostrar_graficas_horizontales(df):

    st.markdown(
        """
        <style>
        .grafica-scroll {
            overflow-x: auto;
            padding-bottom: 10px;
        }

        .grafica-ancha {
            min-width: 1450px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='grafica-scroll'><div class='grafica-ancha'>",
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns([2.6, 1.2, 1.2, 1.2])

    with c1:

        tendencia = (
            df.groupby(df["fecha"].dt.date)[
                [
                    "entrada",
                    "salida",
                    "reserva"
                ]
            ]
            .sum()
            .reset_index()
        )

        tendencia["rotacion"] = (
            tendencia["entrada"]
            +
            tendencia["salida"]
        )

        st.subheader("📈 Tendencia operativa")

        if not tendencia.empty:

            st.area_chart(
                tendencia,
                x="fecha",
                y=[
                    "entrada",
                    "salida"
                ],
                height=320
            )

            st.caption(
                "Visualiza comportamiento operativo y presión diaria del inventario."
            )

        else:

            st.info("No hay datos para tendencia.")

    with c2:

        resumen_tipo = (
            df.groupby("tipo_movimiento_norm")["cantidad"]
            .count()
            .reset_index()
            .rename(
                columns={
                    "tipo_movimiento_norm": "tipo",
                    "cantidad": "movimientos"
                }
            )
            .sort_values(
                "movimientos",
                ascending=False
            )
        )

        st.subheader("📦 Operación")

        if not resumen_tipo.empty:

            st.bar_chart(
                resumen_tipo,
                x="tipo",
                y="movimientos",
                height=320
            )

            tipo_top = resumen_tipo.iloc[0]["tipo"]

            st.success(
                f"Mayor actividad: {tipo_top}"
            )

        else:

            st.info("Sin movimientos.")

    with c3:

        resumen_doc = (
            df.groupby("tipo_documento")["cantidad"]
            .count()
            .reset_index()
            .rename(
                columns={
                    "tipo_documento": "documento",
                    "cantidad": "movimientos"
                }
            )
            .sort_values(
                "movimientos",
                ascending=False
            )
            .head(10)
        )

        st.subheader("📄 Documentos")

        if not resumen_doc.empty:

            st.bar_chart(
                resumen_doc,
                x="documento",
                y="movimientos",
                height=320
            )

            doc_top = resumen_doc.iloc[0]["documento"]

            st.info(
                f"Documento dominante: {doc_top}"
            )

        else:

            st.info("Sin documentos.")

    with c4:

        materiales = (
            df.groupby(
                [
                    "codigo_material",
                    "descripcion"
                ]
            )[
                [
                    "salida",
                    "reserva"
                ]
            ]
            .sum()
            .reset_index()
        )

        materiales["presion"] = (
            materiales["salida"]
            +
            materiales["reserva"]
        )

        materiales["material"] = (
            materiales["codigo_material"].astype(str)
            +
            " - "
            +
            materiales["descripcion"].astype(str).str[:15]
        )

        materiales = materiales.sort_values(
            "presion",
            ascending=False
        ).head(8)

        st.subheader("🔥 Materiales calientes")

        if not materiales.empty:

            st.bar_chart(
                materiales,
                x="material",
                y="presion",
                height=320
            )

            top_material = materiales.iloc[0]["material"]

            st.warning(
                f"Mayor presión: {top_material}"
            )

        else:

            st.info("Sin materiales críticos.")

    st.markdown(
        "</div></div>",
        unsafe_allow_html=True
    )

def mostrar_grid_movimientos(df):

    st.subheader("📋 Movimientos")

    df_grid = df.copy()

    df_grid = df_grid.sort_values(
        by=[
            "fecha",
            "id_movimiento"
        ],
        ascending=[
            False,
            False
        ]
    )

    columnas = [
        "fecha",
        "tipo_movimiento",
        "tipo_documento",
        "numero_documento",
        "folio_movimiento",
        "codigo_material",
        "descripcion",
        "entrada",
        "salida",
        "reserva",
        "impacto_stock",
        "saldo_material_bodega",
        "bodega",
        "ubicacion",
        "referencia",
        "usuario"
    ]

    columnas_existentes = [
        col for col in columnas if col in df_grid.columns
    ]

    st.dataframe(
        df_grid[columnas_existentes],
        use_container_width=True,
        hide_index=True,
        height=420
    )

    csv = df_grid[columnas_existentes].to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "📥 Descargar Kardex filtrado CSV",
        data=csv,
        file_name="kardex_inventario_filtrado.csv",
        mime="text/csv",
        use_container_width=True
    )


def mostrar_subtotales_inferiores(df):

    st.subheader("🧮 Subtotales y corte")

    col_resumen, col_corte = st.columns([4, 1])

    with col_corte:

        corte = st.selectbox(
            "Agrupar por",
            [
                "codigo_material",
                "descripcion",
                "bodega",
                "ubicacion",
                "tipo_movimiento_norm",
                "tipo_documento",
                "numero_documento",
                "usuario"
            ]
        )

    resumen = (
        df.groupby(corte)[
            [
                "entrada",
                "salida",
                "reserva",
                "impacto_stock"
            ]
        ]
        .sum()
        .reset_index()
    )

    resumen["disponible_estimado"] = (
        resumen["impacto_stock"]
        -
        resumen["reserva"]
    )

    resumen = resumen.sort_values(
        by="impacto_stock",
        ascending=False
    )

    total_entradas = df["entrada"].sum()
    total_salidas = df["salida"].sum()
    total_reservas = df["reserva"].sum()
    saldo_final = df["impacto_stock"].sum()
    disponible = saldo_final - total_reservas

    with col_resumen:

        r1, r2, r3, r4, r5 = st.columns(5)

        with r1:
            st.metric(
                "Total entradas",
                f"{total_entradas:,.2f}"
            )

        with r2:
            st.metric(
                "Total salidas",
                f"{total_salidas:,.2f}"
            )

        with r3:
            st.metric(
                "Reservas",
                f"{total_reservas:,.2f}"
            )

        with r4:
            st.metric(
                "Saldo final",
                f"{saldo_final:,.2f}"
            )

        with r5:
            st.metric(
                "Disponible",
                f"{disponible:,.2f}"
            )

    st.dataframe(
        resumen,
        use_container_width=True,
        hide_index=True,
        height=260
    )


def kardex_inventario_app():

    st.set_page_config(
        page_title="Kardex Operativo",
        layout="wide"
    )

    st.title("📒 Kardex Operativo")
    st.caption(
        "Historial de movimientos de inventario con filtros, KPIs, gráficas, movimientos y subtotales."
    )

    try:

        df = obtener_kardex()

        if df.empty:
            st.warning("No existen movimientos de inventario.")
            return

        df = preparar_kardex(df)

        if df.empty:
            st.warning("No hay movimientos válidos para mostrar.")
            return

        col_filtros, col_contenido = st.columns(
            [
                1.15,
                5
            ]
        )

        with col_filtros:

            df_filtrado = aplicar_filtros_laterales(df)

        with col_contenido:

            if df_filtrado.empty:
                st.warning(
                    "No hay movimientos para los filtros seleccionados."
                )
                return

            mostrar_kpis_superiores(df_filtrado)

            st.divider()

            mostrar_graficas_horizontales(df_filtrado)

            st.divider()

            mostrar_grid_movimientos(df_filtrado)

            st.divider()

            mostrar_subtotales_inferiores(df_filtrado)

    except Exception as e:
        st.error("Error consultando Kardex")
        st.exception(e)


if __name__ == "__main__":
    kardex_inventario_app()
