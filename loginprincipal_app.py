import streamlit as st
import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "erp.db"


def validar_login(usuario, password):

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    usuario_limpio = str(usuario).strip().upper()
    password_limpio = str(password).strip()

    try:
        row = cursor.execute(
            """
            SELECT
                usuario,
                nombre,
                password_hash,
                estado,
                id_rol
            FROM usuarios
            WHERE TRIM(UPPER(usuario)) = ?
            """,
            (usuario_limpio,)
        ).fetchone()

    except Exception as e:
        conn.close()
        st.error("❌ Error consultando usuario")
        st.exception(e)
        return None

    conn.close()

    if row is None:
        st.error("❌ Usuario no encontrado")
        return None

    password_bd = str(row["password_hash"]).strip()

    if password_bd != password_limpio:
        st.error("❌ Contraseña incorrecta")
        return None

    if str(row["estado"]).strip().upper() != "ACTIVO":
        st.error("❌ Usuario inactivo")
        return None

    return row


def login_app():

    st.title("🔐 Login SIGEM")

    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar", key="btn_login_sigem"):
        resultado = validar_login(usuario, password)

        if resultado is not None:
            st.session_state.autenticado = True
            st.session_state.usuario = resultado["usuario"]
            st.session_state.nombre = resultado["nombre"]
            st.session_state.rol = resultado["id_rol"]

            st.success("✅ Login correcto")
            st.rerun()


def logout_app():

    if st.sidebar.button("🚪 Cerrar sesión"):
        st.session_state.autenticado = False
        st.session_state.usuario = None
        st.session_state.nombre = None
        st.session_state.rol = None
        st.rerun()


if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    login_app()
    st.stop()


logout_app()

st.success("✅ Usuario autenticado")
st.write("Usuario:", st.session_state.usuario)
st.write("Nombre:", st.session_state.nombre)
st.write("Rol:", st.session_state.rol)
