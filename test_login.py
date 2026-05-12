import streamlit as st
import pandas as pd
import sqlite3

from sigem_db import get_db_path


def test_movimientos_inventario_app():

    st.title("🧪 TEST - movimientos_inventario")

    db_path = get_db_path("inventarios")

    st.subheader("📂 Base utilizada")
    st.code(str(db_path))

    try:

        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # ==========================================
        # VALIDAR EXISTENCIA TABLA
        # ==========================================

        cur.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            AND name='movimientos_inventario'
        """)

        tabla = cur.fetchone()

        if tabla is None:

            st.error(
                "❌ La tabla movimientos_inventario NO existe"
            )

            conn.close()
            return

        st.success(
            "✅ Tabla movimientos_inventario encontrada"
        )

        # ==========================================
        # ESTRUCTURA TABLA
        # ==========================================

        df = pd.read_sql(
            "PRAGMA table_info(movimientos_inventario)",
            conn
        )

        st.subheader("📋 Estructura tabla")

        st.dataframe(
            df,
            use_container_width=True
        )

        columnas = df["name"].tolist()

        st.subheader("📌 Columnas detectadas")

        for col in columnas:

            st.write(f"✅ {col}")

        # ==========================================
        # VALIDAR COLUMNAS REQUERIDAS
        # ==========================================

        columnas_requeridas = [

            "fecha",
            "tipo_movimiento",
            "codigo_material",
            "descripcion",
            "cantidad",
            "costo_unitario",
            "total",
            "bodega",
            "ubicacion",
            "referencia",
            "comentarios",
            "usuario"
        ]

        st.subheader("🔎 Validación columnas")

        faltantes = []

        for col in columnas_requeridas:

            if col in columnas:

                st.success(f"OK -> {col}")

            else:

                st.error(f"FALTA -> {col}")
                faltantes.append(col)

        # ==========================================
        # TEST CONSULTA
        # ==========================================

        st.subheader("📦 Últimos movimientos")

        try:

            query = """
                SELECT *
                FROM movimientos_inventario
                ORDER BY id_movimiento DESC
                LIMIT 20
            """

            df_movs = pd.read_sql(
                query,
                conn
            )

            st.dataframe(
                df_movs,
                use_container_width=True
            )

            st.success(
                f"Movimientos encontrados: {len(df_movs)}"
            )

        except Exception as e:

            st.error(
                "Error consultando movimientos"
            )

            st.exception(e)

        conn.close()

    except Exception as e:

        st.error(
            "Error general validando movimientos_inventario"
        )

        st.exception(e)


if __name__ == "__main__":

    test_movimientos_inventario_app()
