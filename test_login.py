import streamlit as st
import pandas as pd
import sqlite3


def prueba_base_completa():

    st.title("🧪 Prueba completa de base de datos")

    try:
        conn = sqlite3.connect("materiales.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            ORDER BY name
        """)

        tablas = [t[0] for t in cursor.fetchall()]

        st.subheader("📂 Tablas encontradas")
        st.write(tablas)

        if not tablas:
            st.warning("No hay tablas en esta base de datos.")
            return

        for tabla in tablas:
            st.markdown("---")
            st.subheader(f"📋 Tabla: {tabla}")

            df = pd.read_sql_query(f"SELECT * FROM {tabla}", conn)

            st.success(f"Registros encontrados: {len(df)}")
            st.dataframe(df, use_container_width=True)

        conn.close()

    except Exception as e:
        st.error("❌ Error al consultar la base")
        st.exception(e)


if __name__ == "__main__":
    prueba_base_completa()
