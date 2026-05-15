import streamlit as st
import pandas as pd
import sqlite3

from sigem_db import get_db_path


def get_conn_seguridad():

    db_path = get_db_path("seguridad")

    conn = sqlite3.connect(db_path)

    conn.row_factory = sqlite3.Row

    return conn


def normalizar_rol(rol_usuario):

    rol_usuario = str(rol_usuario).strip()

    if rol_usuario == "1":
        return "Admin"

    if rol_usuario == "4":
        return "Logistica"

    return rol_usuario


def sidebar_dinamico():

    rol_usuario = normalizar_rol(
        st.session_state.get("rol", "")
    )

    if not rol_usuario:

        st.sidebar.warning("No hay rol asignado al usuario.")
        return "inicio"

    try:

        conn = get_conn_seguridad()

        menu_df = pd.read_sql_query(
            """
            SELECT DISTINCT
                m.nombre_modulo,
                m.ruta,
                m.orden_menu
            FROM rol_permisos rp
            INNER JOIN roles r
                ON rp.id_rol = r.id_rol
            INNER JOIN modulos m
                ON rp.id_modulo = m.id_modulo
            WHERE r.nombre_rol = ?
              AND rp.puede_ver = 1
              AND IFNULL(m.estado, 'Activo') = 'Activo'
            ORDER BY m.orden_menu
            """,
            conn,
            params=(rol_usuario,)
        )

        conn.close()

    except Exception as e:

        st.sidebar.error("Error leyendo menú dinámico.")
        st.sidebar.exception(e)
        return "inicio"

    if menu_df.empty:

        st.sidebar.warning(
            f"No hay módulos asignados para el rol: {rol_usuario}"
        )

        return "inicio"

    menu_df["nombre_modulo"] = (
        menu_df["nombre_modulo"]
        .astype(str)
        .str.strip()
    )

    menu_df["ruta"] = (
        menu_df["ruta"]
        .astype(str)
        .str.strip()
    )

    menu_df = (
        menu_df
        .sort_values("orden_menu")
        .drop_duplicates(subset=["ruta"])
    )

    opciones = menu_df["nombre_modulo"].tolist()

    if "menu" not in st.session_state:

        st.session_state.menu = opciones[0]

    if st.session_state.menu not in opciones:

        st.session_state.menu = opciones[0]

    with st.sidebar:

        st.title("📌 Navegación")

        menu = st.radio(
            "Menú",
            opciones,
            index=opciones.index(st.session_state.menu)
        )

    st.session_state.menu = menu

    ruta = menu_df[
        menu_df["nombre_modulo"] == menu
    ]["ruta"].iloc[0]

    return ruta
