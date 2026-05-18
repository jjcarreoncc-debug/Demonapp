# crear_admin_seguridad_app.py

import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime


SEGURIDAD_DB_PATH = "/mount/src/demonapp/seguridad.db"


def conectar_seguridad():
    return sqlite3.connect(SEGURIDAD_DB_PATH)


def mostrar_tabla(nombre_tabla):

    conn = conectar_seguridad()

    try:
        df = pd.read_sql_query(f"SELECT * FROM {nombre_tabla}", conn)
        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.warning(f"No se pudo leer la tabla {nombre_tabla}.")
        st.exception(e)

    finally:
        conn.close()


def mostrar_estructura(nombre_tabla):

    conn = conectar_seguridad()

    df = pd.read_sql_query(
        f"PRAGMA table_info({nombre_tabla})",
        conn
    )

    conn.close()

    if df.empty:
        st.warning(f"No se encontró estructura para la tabla {nombre_tabla}.")
    else:
        st.dataframe(df, use_container_width=True)


def crear_usuario_admin():

    conn = conectar_seguridad()
    cur = conn.cursor()

    cur.execute("""
        INSERT OR REPLACE INTO usuarios (
            usuario,
            password,
            nombre,
            email,
            id_rol,
            estado,
            modulo_inicial,
            fecha_creacion
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "admin",
        "admin",
        "Administrador",
        "admin@sigem.com",
        1,
        "Activo",
        "inicio",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def crear_admin_seguridad_app():

    st.title("🔐 Crear usuario administrador")

    st.warning("Este programa está blindado exclusivamente a seguridad.db")

    st.write("📂 Base de datos usada:")
    st.code(SEGURIDAD_DB_PATH)

    if os.path.exists(SEGURIDAD_DB_PATH):
        st.success("✅ seguridad.db existe")
        st.write(f"📦 Tamaño: {os.path.getsize(SEGURIDAD_DB_PATH)} bytes")
    else:
        st.error("❌ seguridad.db NO existe")
        st.stop()

    st.divider()

    st.subheader("📋 Estructura actual usuarios")
    mostrar_estructura("usuarios")

    st.subheader("👤 Datos actuales usuarios")
    mostrar_tabla("usuarios")

    st.divider()

    confirmar = st.checkbox(
        "Confirmo crear/actualizar usuario admin en seguridad.db"
    )

    if not confirmar:
        st.info("Marca la confirmación para habilitar la actualización.")
        st.stop()

    if st.button("✅ Crear / actualizar usuario admin"):

        try:
            crear_usuario_admin()
            st.success("✅ Usuario admin creado/actualizado correctamente")

        except Exception as e:
            st.error("❌ Error creando usuario admin")
            st.exception(e)
            st.stop()

        st.divider()

        st.subheader("👤 Tabla usuarios después de actualizar")
        mostrar_tabla("usuarios")


crear_admin_seguridad_app()
