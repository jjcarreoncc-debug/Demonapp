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

    df["impacto_stock"] = df["entrada"] - df["salida"] + df["ajuste"]

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


def aplicar_filtros(df):

    st.sidebar.header("🔎 Filtros Kardex")

    materiales = ["Todos"] + sorted(
        df["codigo_material"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    material = st.sidebar.selectbox(
        "Material",
        materiales
    )

    bodegas = ["Todas"] + sorted(
        df["bodega"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    bodega = st.sidebar.selectbox(
        "Bodega",
        bodegas
    )

    tipos = ["Todos"] + sorted(
        df["tipo_movimiento_norm"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    tipo = st.sidebar.selectbox(
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

    documento = st.sidebar.selectbox(
        "Tipo documento",
        documentos
    )

    fecha_min = df["fecha"].min().date()
    fecha_max = df["fecha"].max().date()

    rango_fechas = st.sidebar.date_input(
        "Rango de fechas",
        value=(fecha_min, fecha_max)
    )

    texto_busqueda = st.sidebar.text_input(
        "Buscar folio / documento / referencia"
    )

    df_filtrado = df.copy()

    if material != "Todos":
        df_filtrado = df_filtrado[
            df_filtrado["codigo_material"].astype(str) == material
        ]

    if bodega != "Todas":
        df_filtrado = df_filtrado[
            df_filtrado["bodega"].astype(str) == bodega
        ]

    if tipo != "Todos":
        df_filtrado = df_filtrado[
            df_filtrado["tipo_movimiento_norm"].astype(str) == tipo
        ]

    if documento != "Todos":
        df_filtrado = df_filtrado[
            df_filtrado["tipo_documento"].astype(str) == documento
        ]

    if isinstance(rango_fechas, tuple) and len(rango_fechas) == 2:
        fecha_inicio, fecha_fin = rango_fechas

        df_filtrado = df_filtrado[
            (df_filtrado["fecha"].dt.date >= fecha_inicio)
            &
            (df_filtrado["fecha"].dt.date <= fecha_fin)
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

    return df_filtrado


def mostrar_kpis(df):

    entradas = df["entrada"].sum()
    salidas = df["salida"].sum()
    reservas = df["reserva"].sum()
    saldo = df["impacto_stock"].sum()
    disponible = saldo - reservas
    movimientos = len(df)

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        st.metric(
            "Movimientos",
            f"{movimientos:,.0f}"
        )

    with c2:
        st.metric(
            "Entradas",
            f"{entradas:,.2f}"
        )

    with c3:
        st.metric(
            "Salidas",
            f"{salidas:,.2f}"
        )

    with c4:
        st.metric(
            "Reservado",
            f"{reservas:,.2f}"
        )

    with c5:
        st.metric(
            "Saldo físico",
            f"{saldo:,.2f}"
        )

    with c6:
        st.metric(
            "Disponible",
            f"{disponible:,.2f}"
        )


def mostrar_graficas(df):

    st.subheader("📊 Vista gráfica")

    c1, c2 = st.columns(2)

    with c1:

        resumen_tipo = (
            df.groupby("tipo_movimiento_norm")["cantidad"]
            .sum()
            .reset_index()
            .rename(
                columns={
                    "tipo_movimiento_norm": "tipo_movimiento",
                    "cantidad": "cantidad"
                }
            )
        )

        if not resumen_tipo.empty:
            st.markdown("#### Movimientos por tipo")
            st.bar_chart(
                resumen_tipo,
                x="tipo_movimiento",
                y="cantidad"
            )

    with c2:

        resumen_bodega = (
            df.groupby("bodega")["impacto_stock"]
            .sum()
            .reset_index()
            .rename(
                columns={
                    "impacto_stock": "saldo"
                }
            )
        )

        if not resumen_bodega.empty:
            st.markdown("#### Saldo por bodega")
            st.bar_chart(
                resumen_bodega,
                x="bodega",
                y="saldo"
            )

    tendencia = (
        df.groupby(df["fecha"].dt.date)[["entrada", "salida", "reserva"]]
        .sum()
        .reset_index()
        .rename(columns={"fecha": "fecha"})
    )

    if not tendencia.empty:
        st.markdown("#### Tendencia diaria")
        st.line_chart(
            tendencia,
            x="fecha",
            y=[
                "entrada",
                "salida",
                "reserva"
            ]
        )


def mostrar_subtotales(df):

    st.subheader("🧮 Subtotales dinámicos")

    corte = st.selectbox(
        "Cortar subtotales por",
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

    st.dataframe(
        resumen,
        use_container_width=True,
        hide_index=True
    )


def mostrar_grid(df):

    st.subheader("📋 Movimientos del Kardex")

    columnas = [
        "id_movimiento",
        "folio_movimiento",
        "fecha",
        "tipo_movimiento",
        "tipo_documento",
        "numero_documento",
        "codigo_material",
        "descripcion",
        "cantidad",
        "entrada",
        "salida",
        "reserva",
        "impacto_stock",
        "saldo_material_bodega",
        "bodega",
        "ubicacion",
        "referencia",
        "comentarios",
        "usuario"
    ]

    columnas_existentes = [
        col for col in columnas if col in df.columns
    ]

    st.dataframe(
        df[columnas_existentes],
        use_container_width=True,
        hide_index=True
    )

    csv = df[columnas_existentes].to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "📥 Descargar Kardex filtrado CSV",
        data=csv,
        file_name="kardex_inventario_filtrado.csv",
        mime="text/csv",
        use_container_width=True
    )


def mostrar_detalle_material(df):

    st.subheader("🔍 Detalle por material")

    materiales = sorted(
        df["codigo_material"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    if not materiales:
        st.info("No hay materiales en el filtro actual.")
        return

    material_sel = st.selectbox(
        "Selecciona material",
        materiales,
        key="detalle_material_kardex"
    )

    df_mat = df[
        df["codigo_material"].astype(str) == material_sel
    ].copy()

    if df_mat.empty:
        st.warning("No hay movimientos para el material seleccionado.")
        return

    descripcion = df_mat["descripcion"].dropna().astype(str).iloc[0]

    st.markdown(f"### {material_sel} - {descripcion}")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Entradas",
            f"{df_mat['entrada'].sum():,.2f}"
        )

    with c2:
        st.metric(
            "Salidas",
            f"{df_mat['salida'].sum():,.2f}"
        )

    with c3:
        st.metric(
            "Reservado",
            f"{df_mat['reserva'].sum():,.2f}"
        )

    with c4:
        st.metric(
            "Disponible",
            f"{(df_mat['impacto_stock'].sum() - df_mat['reserva'].sum()):,.2f}"
        )

    resumen_bodega = (
        df_mat.groupby("bodega")[
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

    resumen_bodega["disponible_estimado"] = (
        resumen_bodega["impacto_stock"]
        -
        resumen_bodega["reserva"]
    )

    st.markdown("#### Resumen por bodega")
    st.dataframe(
        resumen_bodega,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("#### Movimientos del material")
    mostrar_grid(df_mat)


def kardex_inventario_app():

    st.title("📒 Kardex Inventario")

    st.caption(
        "Vista operativa de movimientos, entradas, salidas, reservas y saldos por material y bodega."
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

        df_filtrado = aplicar_filtros(df)

        if df_filtrado.empty:
            st.warning("No hay movimientos para los filtros seleccionados.")
            return

        mostrar_kpis(df_filtrado)

        st.divider()

        tab_dashboard, tab_grid, tab_subtotales, tab_material = st.tabs(
            [
                "📊 Dashboard",
                "📋 Movimientos",
                "🧮 Subtotales",
                "🔍 Material"
            ]
        )

        with tab_dashboard:
            mostrar_graficas(df_filtrado)

        with tab_grid:
            mostrar_grid(df_filtrado)

        with tab_subtotales:
            mostrar_subtotales(df_filtrado)

        with tab_material:
            mostrar_detalle_material(df_filtrado)

    except Exception as e:
        st.error("Error consultando Kardex")
        st.exception(e)


if __name__ == "__main__":
    kardex_inventario_app()
