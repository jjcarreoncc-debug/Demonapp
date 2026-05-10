import streamlit as st
import pandas as pd
import sqlite3


def prueba_tabla_materiales():

    st.title("🧪 Prueba tabla materiales")

    try:

        # CAMBIA EL NOMBRE SI TU BD SE LLAMA DIFERENTE
        conn = sqlite3.connect("materiales.db")

        cursor = conn.cursor()

        # VER TABLAS EXISTENTES
        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type='table'
        """)

        tablas = cursor.fetchall()

        st.subheader("📂 Tablas encontradas")
        st.write(tablas)

        # CONSULTAR REGISTROS
        query = "SELECT * FROM materiales"

        df = pd.read_sql_query(query, conn)

        st.subheader("📊 Total registros")
        st.success(f"Registros encontrados: {len(df)}")

        st.subheader("📋 Datos")

        st.dataframe(
            df,
            use_container_width=True
        )

        conn.close()

    except Exception as e:

        st.error("❌ Error al consultar la base")
        st.exception(e)


if __name__ == "__main__":
    prueba_tabla_materiales()
