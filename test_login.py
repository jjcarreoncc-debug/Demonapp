import streamlit as st
import sqlite3
import pandas as pd
from sigem_db import get_db_path


st.set_page_config(
    page_title="Comparativo Bases",
    layout="wide"
)

st.title("🔎 Comparativo ERP vs SEGURIDAD")

bases = [
    ("ERP", "erp"),
    ("SEGURIDAD", "seguridad")
]

for nombre_base, clave in bases:

    st.divider()
    st.header(f"📦 Base: {nombre_base}")

    try:

        db_path = get_db_path(clave)

        st.success(f"Ruta detectada: {db_path}")

        conn = sqlite3.connect(db_path)

        tablas = pd.read_sql_query(
            """
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            ORDER BY name
            """,
            conn
        )

        if tablas.empty:

            st.warning("No se encontraron tablas.")

        else:

            st.subheader("📋 Tablas")

            st.dataframe(
                tablas,
                use_container_width=True
            )

            for tabla in tablas["name"].tolist():

                st.markdown(f"### 📌 {tabla}")

                try:

                    estructura = pd.read_sql_query(
                        f"""
                        PRAGMA table_info({tabla})
                        """,
                        conn
                    )

                    st.write("Estructura:")

                    st.dataframe(
                        estructura,
                        use_container_width=True
                    )

                    try:

                        datos = pd.read_sql_query(
                            f"""
                            SELECT *
                            FROM {tabla}
                            LIMIT 5
                            """,
                            conn
                        )

                        st.write("Datos:")

                        st.dataframe(
                            datos,
                            use_container_width=True
                        )

                    except Exception as e:

                        st.error(
                            f"No se pudieron leer datos: {e}"
                        )

                except Exception as e:

                    st.error(
                        f"No se pudo leer estructura: {e}"
                    )

        conn.close()

    except Exception as e:

        st.error(f"Error abriendo base {nombre_base}")
        st.exception(e)
