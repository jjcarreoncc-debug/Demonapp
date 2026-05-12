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
        ORDER BY codigo_material, fecha, id_movimiento
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    return df


def kardex_inventario_app():

    st.title("📒 Kardex Inventario")

    try:
        df = obtener_kardex()

        if df.empty:
            st.warning("No existen movimientos de inventario.")
            return

        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
        df = df.dropna(subset=["fecha"])

        st.subheader("🔎 Filtros")

        c1, c2 = st.columns(2)

        with c1:
            materiales = ["Todos"] + sorted(
                df["codigo_material"].dropna().unique().tolist()
            )

            material = st.selectbox(
                "Material",
                materiales
            )

        with c2:
            fecha_min = df["fecha"].min().date()
            fecha_max = df["fecha"].max().date()

            rango_fechas = st.date_input(
                "Rango de fechas",
                value=(fecha_min, fecha_max)
            )

        if material != "Todos":
            df = df[df["codigo_material"] == material]

        if isinstance(rango_fechas, tuple) and len(rango_fechas) == 2:
            fecha_inicio, fecha_fin = rango_fechas

            df = df[
                (df["fecha"].dt.date >= fecha_inicio)
                &
                (df["fecha"].dt.date <= fecha_fin)
            ]

        if df.empty:
            st.warning("No hay movimientos para los filtros seleccionados.")
            return

        df = df.sort_values(
            by=["codigo_material", "fecha", "id_movimiento"]
        )

        df["entrada"] = df["cantidad"].apply(
            lambda x: x if x > 0 else 0
        )

        df["salida"] = df["cantidad"].apply(
            lambda x: abs(x) if x < 0 else 0
        )

        df["saldo"] = df.groupby("codigo_material")["cantidad"].cumsum()

        columnas = [
            "id_movimiento",
            "folio_movimiento",
            "fecha",
            "tipo_movimiento",
            "tipo_documento",
            "numero_documento",
            "codigo_material",
            "descripcion",
            "entrada",
            "salida",
            "saldo",
            "bodega",
            "ubicacion",
            "referencia",
            "comentarios",
            "usuario"
        ]

        columnas_existentes = [
            col for col in columnas if col in df.columns
        ]

        st.subheader("📋 Detalle Kardex")

        st.dataframe(
            df[columnas_existentes],
            use_container_width=True
        )

        st.subheader("📊 Resumen")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric("Entradas", df["entrada"].sum())

        with c2:
            st.metric("Salidas", df["salida"].sum())

        with c3:
            st.metric("Saldo", df["cantidad"].sum())

    except Exception as e:
        st.error("Error consultando Kardex")
        st.exception(e)


if __name__ == "__main__":
    kardex_inventario_app()
