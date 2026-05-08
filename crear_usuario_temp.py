import streamlit as st
import pandas as pd

from database import get_connection

st.title("Dar permisos Admin a cvazquez")

conn = get_connection()

st.subheader("Antes")
usuarios = pd.read_sql("SELECT * FROM usuarios", conn)
st.dataframe(usuarios)

if st.button("Actualizar cvazquez a Admin"):
    try:
        conn.execute("""
            UPDATE usuarios
            SET 
                password_hash = 'Roberto1',
                estado = 'Activo',
                id_rol = 1
            WHERE usuario = 'cvazquez'
        """)

        conn.commit()

        st.success("cvazquez actualizado: password Roberto1, estado Activo, rol Admin")

    except Exception as e:
        st.error(f"Error: {e}")

st.subheader("Después")
usuarios2 = pd.read_sql("SELECT * FROM usuarios", conn)
st.dataframe(usuarios2)

conn.close()
