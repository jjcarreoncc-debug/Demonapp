
import streamlit as st
import sqlite3
from pathlib import Path


st.title("🧪 Buscar base con usuarios")


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = str(BASE_DIR / "erp.db")

st.write("Carpeta:")
st.code(str(BASE_DIR))

dbs = list(BASE_DIR.glob("*.db"))

st.write("Bases encontradas:")
for db in dbs:
    st.write(db.name)

st.markdown("---")

for db in dbs:
    st.subheader(f"📂 {db.name}")

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        tablas = cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            ORDER BY name
        """).fetchall()

        nombres_tablas = [t["name"] for t in tablas]

        st.write("Tablas:")
        st.write(nombres_tablas)

        if "usuarios" in nombres_tablas:
            st.success("✅ Esta base tiene usuarios")

            usuarios = cursor.execute("""
                SELECT usuario, nombre, password_hash, estado, id_rol
                FROM usuarios
            """).fetchall()

            for u in usuarios:
                st.write(dict(u))
        else:
            st.warning("No tiene tabla usuarios")

        conn.close()

    except Exception as e:
        st.error("Error leyendo base")
        st.exception(e)
