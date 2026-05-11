import streamlit as st
import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "erp.db"


def validar_login(usuario, password):

    st.write("🔎 Entrando a validar_login()")
    st.write("📂 Ruta BD:")
    st.code(str(DB_PATH))

    st.write("📦 Existe BD:")
    st.write(DB_PATH.exists())

    if DB_PATH.exists():
        st.write("📏 Tamaño BD:")
        st.write(DB_PATH.stat().st_size)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    st.write("✅ Conexión SQLite abierta")

    usuario_limpio = str(usuario).strip().upper()
    password_limpio = str(password).strip()

    st.write("👤 Usuario recibido:")
    st.code(usuario)

    st.write("👤 Usuario limpio:")
    st.code(usuario_limpio)

    try:
        st.write("📋 Leyendo tablas existentes...")

        tablas = cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            ORDER BY name
        """).fetchall()

        st.write("📋 Tablas encontradas:")
        st.write([t["name"] for t in tablas])

        st.write("🔐 Ejecutando SELECT usuarios...")

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

        st.write("✅ SELECT terminado")

    except Exception as e:
        conn.close()
        st.error("❌ Error consultando usuario")
        st.exception(e)
        st.write("🚪 Saliendo de validar_login() por error SQL")
        return None

    conn.close()
    st.write("✅ Conexión SQLite cerrada")

    if row is None:
        st.error("❌ Usuario no encontrado")
        st.write("🚪 Saliendo de validar_login(): usuario no existe")
        return None

    st.success("✅ Usuario encontrado")
    st.write("🧾 Datos usuario:")
    st.write(dict(row))

    password_bd = str(row["password_hash"]).strip()

    st.write("🔑 Password BD:")
    st.code(password_bd)

    st.write("🔑 Password ingresado:")
    st.code(password_limpio)

    if password_bd != password_limpio:
        st.error("❌ Contraseña incorrecta")
        st.write("🚪 Saliendo de validar_login(): password incorrecto")
        return None

    if str(row["estado"]).strip().upper() != "ACTIVO":
        st.error("❌ Usuario inactivo")
        st.write("🚪 Saliendo de validar_login(): usuario inactivo")
        return None

    st.success("✅ Login validado correctamente")
    st.write("🚪 Saliendo de validar_login(): OK")

    return row


def login_app():

    st.title("🔐 Login SIGEM")

    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar", key="btn_login_sigem"):
        st.write("🟦 Botón Ingresar presionado")

        resultado = validar_login(usuario, password)

        st.write("📤 Resultado validar_login():")
        st.write(resultado)

        if resultado is not None:
            st.session_state.autenticado = True
            st.session_state.usuario = resultado["usuario"]
            st.session_state.nombre = resultado["nombre"]
            st.session_state.rol = resultado["id_rol"]

            st.success("✅ Login correcto")
            st.rerun()
        else:
            st.error("❌ Login no autorizado")


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
