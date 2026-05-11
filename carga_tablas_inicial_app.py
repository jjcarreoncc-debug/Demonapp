import streamlit as st
import pandas as pd
import sqlite3

from sigem_db import get_db_path


def carga_tablas_inicial_app():

    st.title("📥 Carga tablas inicial")

    modulo = st.selectbox(
        "Módulo",
        ["Inventarios"]
    )

    tabla = st.selectbox(
        "Tabla destino",
        ["materiales"]
    )

    archivo = st.file_uploader(
        "Selecciona archivo CSV o Excel",
        type=["csv", "xlsx"]
    )

    if archivo is None:
        st.info("Carga un archivo para iniciar.")
        return

    if archivo.name.lower().endswith(".csv"):
        df = pd.read_csv(archivo)
    else:
        df = pd.read_excel(archivo)

    st.success(f"Archivo leído: {len(df)} registros")
    st.dataframe(df.head(), use_container_width=True)

    db_path = get_db_path("materiales")

    st.write("Base destino:")
    st.code(str(db_path))

    if st.button("🚀 Cargar a tabla"):

        conn = sqlite3.connect(db_path)

        df.to_sql(
            tabla,
            conn,
            if_exists="append",
            index=False
        )

        conn.close()

        st.success("✅ Carga realizada")
