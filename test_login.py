import streamlit as st
import sqlite3
import os


st.title("🧪 Diagnóstico materiales.db")

ruta = os.path.abspath("materiales.db")

st.write("📂 Ruta completa:")
st.code(ruta)

st.write("📏 Existe archivo:")
st.write(os.path.exists("materiales.db"))

st.write("📦 Tamaño:")
st.write(os.path.getsize("materiales.db"))

conn = sqlite3.connect("materiales.db")

cursor = conn.cursor()

cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type='table'
""")

tablas = cursor.fetchall()

st.write("📋 Tablas:")
st.write(tablas)

conn.close()
