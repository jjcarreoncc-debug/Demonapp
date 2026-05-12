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

        materiales = ["Todos"] + sorted(df["codigo_material"].dropna().unique().tolist())

        material = st.selectbox(
            "Filtrar material",
            materiales
        )

        if material != "Todos":
            df = df[df["codigo_material"] == material]

        df["entrada"] = df["cantidad"].apply(lambda x: x if x > 0 else 0)
        df["salida"] = df["cantidad"].apply(lambda x: abs(x) if x < 0 else 0)
        df["saldo"] = df.groupby("codigo_material")["cantidad"].cumsum()

        st.dataframe(
            df,
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
