import streamlit as st
from sidebar_inventarios import sidebar_inventarios

st.set_page_config(
    page_title="SIGEM Inventarios",
    layout="wide"
)

subopcion_inv = sidebar_inventarios()

st.title("📦 Inventarios")
st.subheader(subopcion_inv)
