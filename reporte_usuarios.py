import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "erp.db"


def reporte_usuarios_app():

    st.title("👥 Reporte de usuarios")

    conn = sqlite3.connect(DB_PATH)

    query = """
        SELECT
            u.id_usuario,
            u.usuario,
            u.nombre,
            u.email,
            u.estado,
            u.id_rol,
            r.nombre_rol,
            u.modulo_inicial,
            u.fecha_creacion,
            u.ultimo_login
        FROM usuarios u
        LEFT JOIN roles r
            ON u.id_rol = r.id_rol
        ORDER BY u.id_usuario
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    st.success(f"Usuarios encontrados: {len(df)}")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


if __name__ == "__main__":
    reporte_usuarios_app()
