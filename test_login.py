import streamlit as st
import pandas as pd
from database import get_connection

st.title("TEST USUARIOS")

conn = get_connection()

st.subheader("Estructura usuarios")
st.dataframe(
    pd.read_sql_query("PRAGMA table_info(usuarios)", conn),
    use_container_width=True
)

st.subheader("Datos usuarios")
st.dataframe(
    pd.read_sql_query("SELECT * FROM usuarios", conn),
    use_container_width=True
)

conn.close()
