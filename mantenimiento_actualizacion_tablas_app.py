import streamlit as st
import sqlite3
from pathlib import Path
import pandas as pd


def actualizacion_tablas_app():

    st.subheader("🗄️ Actualización de tablas")

    BASE_DIR = Path(__file__).resolve().parent

    archivos_db = list(BASE_DIR.glob("*.db"))

    if not archivos_db:
        st.warning("No se encontraron bases de datos.")
        return

    data = []

    for db_file in archivos_db:

        try:

            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()

            tablas = cursor.execute("""
                SELECT name
                FROM sqlite_master
                WHERE type='table'
                ORDER BY name
            """).fetchall()

            conn.close()

            nombres_tablas = ", ".join(
                [t[0] for t in tablas]
            )

            data.append({
                "Base de datos": db_file.name,
                "Ruta": str(db_file),
                "Tamaño KB": round(db_file.stat().st_size / 1024, 2),
                "Tablas": nombres_tablas
            })

        except Exception as e:

            data.append({
                "Base de datos": db_file.name,
                "Ruta": str(db_file),
                "Tamaño KB": 0,
                "Tablas": f"ERROR: {e}"
            })

    df = pd.DataFrame(data)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    st.info(
        "Aquí se administrarán las conexiones, tablas y rutas SIGEM."
    )
