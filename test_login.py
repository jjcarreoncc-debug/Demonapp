import sqlite3
import streamlit as st

from sigem_db import get_db_path


def insertar_roles():

    db_path = get_db_path("seguridad")

    st.info(f"Base: {db_path}")

    conn = sqlite3.connect(db_path)

    cur = conn.cursor()

    roles = [

        ("Admin", "Administrador del sistema"),
        ("Gerencia", "Gerencia general"),
        ("Compras", "Modulo compras"),
        ("Logistica", "Modulo logistica"),
        ("WMS", "Modulo almacen WMS"),
        ("Consulta", "Solo consulta")

    ]

    for nombre_rol, descripcion in roles:

        cur.execute("""
            INSERT OR IGNORE INTO roles (
                nombre_rol,
                descripcion
            )
            VALUES (?, ?)
        """, (
            nombre_rol,
            descripcion
        ))

        st.success(f"✅ Rol insertado: {nombre_rol}")

    conn.commit()
    conn.close()

    st.success("✅ Proceso terminado")


insertar_roles()
