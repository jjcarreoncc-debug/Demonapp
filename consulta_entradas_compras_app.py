import streamlit as st
import pandas as pd
import sqlite3

from sigem_db import get_db_path
from compras_db import crear_tablas_compras


def consulta_entradas_compras_app():

    st.title("📋 Consulta entradas compra")

    try:
        crear_tablas_compras()

        db_path = get_db_path("compras")

        conn = sqlite3.connect(db_path)

        query = """
            SELECT
                e.id_entrada,
                e.proveedor,
                e.factura,
                e.fecha_factura,
                e.fecha_recepcion,
                e.moneda,
                d.codigo_material,
                d.descripcion,
                d.cantidad,
                d.costo_unitario,
                d.impuesto,
                d.total,
                d.bodega,
                d.ubicacion,
                e.archivo_adjunto,
                e.fecha_creacion,
                e.usuario_creacion
            FROM entradas_compras e
            LEFT JOIN entradas_compras_detalle d
                ON e.id_entrada = d.id_entrada
            ORDER BY e.id_entrada DESC
        """

        df = pd.read_sql_query(query, conn)
        conn.close()

        st.success(f"Registros encontrados: {len(df)}")

        st.dataframe(
            df,
            use_container_width=True
        )

        if not df.empty:
            st.subheader("📊 Resumen")

            total_piezas = df["cantidad"].fillna(0).sum()
            total_importe = df["total"].fillna(0).sum()

            c1, c2, c3 = st.columns(3)

            with c1:
                st.metric("Total piezas", total_piezas)

            with c2:
                st.metric("Total importe", total_importe)

            with c3:
                st.metric("Facturas", df["factura"].nunique())

    except Exception as e:
        st.error("Error consultando entradas compra")
        st.exception(e)


if __name__ == "__main__":
    consulta_entradas_compras_app()
