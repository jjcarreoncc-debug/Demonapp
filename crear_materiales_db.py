import streamlit as st

from materiales_db import crear_tabla_materiales


st.title("🛠️ Crear tabla materiales")


if st.button("🚀 Crear tabla"):

    try:

        crear_tabla_materiales()

        st.success("✅ Tabla materiales creada")

    except Exception as e:

        st.error("❌ Error creando tabla")

        st.exception(e)
