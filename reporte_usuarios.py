import streamlit as st
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

st.title("🧪 Diagnóstico bases de datos")

st.write("Carpeta actual:")
st.code(str(BASE_DIR))

st.subheader("Archivos .db encontrados")

dbs = list(BASE_DIR.glob("*.db"))

if not dbs:
    st.error("No encontré archivos .db en esta carpeta.")

for db in dbs:
    st.markdown("---")
    st.write(f"📂 {db.name}")
    st.write(f"Ruta: {db}")
    st.write(f"Tamaño: {db.stat().st_size} bytes")

    try:
        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            ORDER BY name
        """)

        tablas = [t[0] for t in cursor.fetchall()]
        conn.close()

        st.write("Tablas:")
        st.write(tablas)

    except Exception as e:
        st.error("Error leyendo base")
        st.exception(e)
