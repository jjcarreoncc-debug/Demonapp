import streamlit as st
import pandas as pd

from database import get_connection


def sidebar_dinamico():

    conn = get_connection()

    menu_df = pd.read_sql_query(
        """
        SELECT DISTINCT
            m.nombre_modulo,
            m.icono,
            m.ruta,
            m.orden_menu
        FROM permisos_roles pr
        INNER JOIN roles r
            ON pr.id_rol = r.id_rol
        INNER JOIN modulos m
            ON pr.id_modulo = m.id_modulo
        WHERE r.nombre_rol = ?
        AND pr.puede_ver = 1
        AND m.activo = 1
        ORDER BY m.orden_menu
        """,
        conn,
        params=(st.session_state.rol,)
    )

    conn.close()

    if menu_df.empty:
        st.sidebar.warning("No hay módulos asignados a este rol.")
        return "inicio"

    menu_df["nombre_modulo"] = menu_df["nombre_modulo"].astype(str).str.strip()
    menu_df["ruta"] = menu_df["ruta"].astype(str).str.strip()

    menu_df = (
        menu_df
        .sort_values("orden_menu")
        .drop_duplicates(subset=["nombre_modulo"])
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

    fila = menu_df[menu_df["nombre_modulo"] == menu]

    if fila.empty:
        st.error(f"No encontré ruta para el módulo: {menu}")
        return "inicio"

    ruta = fila["ruta"].iloc[0]

    if ruta in ["", "None", "nan"]:
        st.error(f"El módulo '{menu}' no tiene ruta configurada.")
        return "inicio"

    return ruta
