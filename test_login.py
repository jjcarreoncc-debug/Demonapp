import streamlit as st
import sqlite3
import pandas as pd
from sigem_db import get_db_path


st.set_page_config(
    page_title="Test BD Seguridad",
    layout="wide"
)


st.title("🔎 Test Base de Datos Seguridad")

try:
    db_path = get_db_path("seguridad")

    st.success("Ruta detectada:")
    st.code(db_path)

    conn = sqlite3.connect(db_path)

    tablas = pd.read_sql_query(
        """
        SELECT name AS tabla
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
        """,
        conn
    )

    st.subheader("📋 Tablas encontradas")

    if tablas.empty:
        st.error("No se encontraron tablas en esta base.")
    else:
        st.dataframe(tablas, use_container_width=True)

        for tabla in tablas["tabla"].tolist():

            st.divider()
            st.subheader(f"📌 Tabla: {tabla}")

            try:
                df = pd.read_sql_query(
                    f"SELECT * FROM {tabla} LIMIT 20",
                    conn
                )

                st.write(f"Registros encontrados: {len(df)}")
                st.dataframe(df, use_container_width=True)

            except Exception as e:
                st.error(f"No se pudo leer la tabla {tabla}: {e}")

    conn.close()

except Exception as e:
    st.error("Error general revisando la base de seguridad")
    st.exception(e)
