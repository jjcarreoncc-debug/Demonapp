import streamlit as st
import pandas as pd

from database import get_connection


def diagnostico_tablas_app():

    st.title("🔎 Diagnóstico de tablas dinámicas")

    conn = get_connection()

    st.markdown("## 🧱 Tabla modulos")

    modulos_df = pd.read_sql_query(
        """
        SELECT *
        FROM modulos
        ORDER BY nombre_modulo, id_modulo
        """,
        conn
    )

    st.dataframe(
        modulos_df,
        use_container_width=True
    )

    st.markdown("## 🔐 Tabla permisos_roles")

    permisos_df = pd.read_sql_query(
        """
        SELECT *
        FROM permisos_roles
        ORDER BY id_rol, id_modulo
        """,
        conn
    )

    st.dataframe(
        permisos_df,
        use_container_width=True
    )

    st.markdown("## 🔗 Vista permisos con nombres")

    vista_df = pd.read_sql_query(
        """
        SELECT
            pr.id_permiso,
            r.id_rol,
            r.nombre_rol,
            m.id_modulo,
            m.nombre_modulo,
            m.ruta,
            m.activo,
            pr.puede_ver
        FROM permisos_roles pr
        LEFT JOIN roles r
            ON pr.id_rol = r.id_rol
        LEFT JOIN modulos m
            ON pr.id_modulo = m.id_modulo
        ORDER BY r.nombre_rol, m.nombre_modulo
        """,
        conn
    )

    st.dataframe(
        vista_df,
        use_container_width=True
    )

    st.markdown("## ⚠️ Posibles módulos duplicados")

    duplicados_df = pd.read_sql_query(
        """
        SELECT
            nombre_modulo,
            ruta,
            COUNT(*) AS cantidad
        FROM modulos
        GROUP BY nombre_modulo, ruta
        HAVING COUNT(*) > 1
        ORDER BY cantidad DESC
        """,
        conn
    )

    st.dataframe(
        duplicados_df,
        use_container_width=True
    )

    conn.close()
