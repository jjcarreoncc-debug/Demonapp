import streamlit as st
import sqlite3
import pandas as pd

from sigem_db import get_db_path

from compras_db import crear_tablas_compras

from inventario_db import (
    crear_tablas_inventario,
    crear_tabla_movimientos_inventario
)


def mostrar_estructura_tabla(db_path, tabla):

    conn = sqlite3.connect(db_path)

    df = pd.read_sql_query(
        f"PRAGMA table_info({tabla})",
        conn
    )

    conn.close()

    if df.empty:
        st.warning("No se encontró estructura para esta tabla.")
    else:
        st.dataframe(df, use_container_width=True)


def alterar_movimientos_inventario():

    db_path = get_db_path("inventarios")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    st.subheader("📋 Estructura actual")
    mostrar_estructura_tabla(db_path, "movimientos_inventario")

    columnas_nuevas = [
        ("folio_movimiento", "TEXT"),
        ("tipo_documento", "TEXT"),
        ("numero_documento", "TEXT"),
        ("archivo_documento", "TEXT"),
        ("referencia", "TEXT"),
        ("comentarios", "TEXT"),
        ("usuario", "TEXT"),
    ]

    st.subheader("🔧 Columnas a validar/agregar")

    for nombre_columna, tipo_columna in columnas_nuevas:

        try:

            cur.execute(
                f"""
                ALTER TABLE movimientos_inventario
                ADD COLUMN {nombre_columna} {tipo_columna}
                """
            )

            st.success(f"✅ Columna agregada: {nombre_columna}")

        except sqlite3.OperationalError:

            st.info(f"ℹ️ La columna ya existe: {nombre_columna}")

    conn.commit()
    conn.close()

    st.subheader("📋 Estructura final")
    mostrar_estructura_tabla(db_path, "movimientos_inventario")


def crear_tablas_app():

    st.title("🗄️ Crear / modificar tablas")

    tipo_proceso = st.selectbox(
        "Tipo proceso",
        [
            "Crear tabla",
            "Modificar estructura"
        ],
        key="tipo_proceso_tablas"
    )

    modulo = st.selectbox(
        "Selecciona módulo",
        [
            "Compras",
            "Inventarios"
        ],
        key="crear_tablas_modulo"
    )

    tablas_disponibles = []

    if modulo == "Compras":

        tablas_disponibles = [
            "Todas",
            "entradas_compras",
            "entradas_compras_detalle"
        ]

    elif modulo == "Inventarios":

        tablas_disponibles = [
            "Todas",
            "materiales",
            "movimientos_inventario"
        ]

    tabla = st.selectbox(
        "Selecciona tabla",
        tablas_disponibles,
        key="crear_tablas_tabla"
    )

    if tipo_proceso == "Crear tabla":

        st.info(
            "Este proceso crea únicamente la tabla seleccionada si no existe."
        )

        if st.button("🚀 Crear tablas", key="btn_crear_tablas"):

            try:

                if modulo == "Compras":

                    crear_tablas_compras()

                elif modulo == "Inventarios":

                    if tabla == "Todas":

                        crear_tablas_inventario()
                        crear_tabla_movimientos_inventario()

                    elif tabla == "materiales":

                        crear_tablas_inventario()

                    elif tabla == "movimientos_inventario":

                        crear_tabla_movimientos_inventario()

                st.success(
                    f"✅ Tabla(s) creadas correctamente para {modulo}"
                )

            except Exception as e:

                st.error(
                    f"❌ Error creando tablas del módulo {modulo}"
                )

                st.exception(e)

    elif tipo_proceso == "Modificar estructura":

        st.warning(
            "Este proceso modifica la estructura de una tabla existente sin borrar datos."
        )

        if modulo == "Inventarios" and tabla == "movimientos_inventario":

            if st.button("🛠️ Modificar estructura", key="btn_alter_mov_inv"):

                try:

                    alterar_movimientos_inventario()

                    st.success(
                        "✅ Estructura de movimientos_inventario actualizada"
                    )

                except Exception as e:

                    st.error(
                        "❌ Error modificando movimientos_inventario"
                    )

                    st.exception(e)

        else:

            st.info(
                "Por ahora la modificación de estructura está habilitada solo para Inventarios / movimientos_inventario."
            )
