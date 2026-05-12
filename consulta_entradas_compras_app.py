import streamlit as st
import pandas as pd
import sqlite3

from sigem_db import get_db_path


def consulta_entradas_compras_app():

    st.title("📋 Consulta entradas compra")

    try:

        db_path = get_db_path("compras")

        conn = sqlite3.connect(db_path)

        query = """
            SELECT
                id_entrada,
                proveedor,
                factura,
                fecha_factura,
                fecha_recepcion,
                moneda,
                total,
                archivo_adjunto,
                fecha_creacion
            FROM entradas_compras
            ORDER BY id_entrada DESC
        """

        df = pd.read_sql_query(query, conn)

        conn.close()

        st.success(
            f"Registros encontrados: {len(df)}"
        )

        st.dataframe(
            df,
            use_container_width=True
        )

    except Exception as e:

        st.error(
            "Error consultando entradas compra"
        )

        st.exception(e)


if __name__ == "__main__":
    consulta_entradas_compras_app()
