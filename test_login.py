
import streamlit as st
import sqlite3


st.title("🔍 Test materiales.db")


DB_PATH = "/mount/src/demonapp/materiales.db"


st.write("📂 Ruta:")
st.code(DB_PATH)


try:

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    # =========================
    # VER TABLAS
    # =========================
    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
    """)

    tablas = cursor.fetchall()

    st.subheader("📋 Tablas encontradas")

    st.write(tablas)

    # =========================
    # VER MATERIALES
    # =========================
    cursor.execute("""
        SELECT *
        FROM materiales
    """)

    registros = cursor.fetchall()

    st.subheader("📦 Registros materiales")

    st.write(f"Total registros: {len(registros)}")

    st.dataframe(registros)

    conn.close()

except Exception as e:

    st.error("❌ Error leyendo materiales.db")

    st.exception(e)
