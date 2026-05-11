
import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "erp.db"

conn = sqlite3.connect(DB_PATH)

st.title("🧪 Permisos por rol")

st.subheader("Usuarios")
st.dataframe(pd.read_sql_query("SELECT * FROM usuarios", conn))

st.subheader("Roles")
st.dataframe(pd.read_sql_query("SELECT * FROM roles", conn))

st.subheader("Módulos")
st.dataframe(pd.read_sql_query("SELECT * FROM modulos", conn))

st.subheader("Permisos roles")
st.dataframe(pd.read_sql_query("SELECT * FROM permisos_roles", conn))

conn.close()
