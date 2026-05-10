import streamlit as st
import pandas as pd
import sqlite3


def consulta_material_app():
    st.title("🔍 Consulta de materiales")

    conn = sqlite3.connect("materiales.db")

    df = pd.read_sql_query(
        "SELECT * FROM materiales ORDER BY codigo_material",
        conn
    )

    conn.close()

    st.success(f"Registros encontrados: {len(df)}")
    st.dataframe(df, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    consulta_material_app()
