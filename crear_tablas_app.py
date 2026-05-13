import streamlit as st
import sqlite3
import pandas as pd

from sigem_db import get_db_path

from compras_db import crear_tablas_compras

from inventario_db import (
    crear_tablas_inventario,
    crear_tabla_movimientos_inventario,
    crear_tabla_inventario_fisico
)


def mostrar_estructura_tabla(db_path, tabla):

    st.title("🗄️ Crear / modificar tablas")

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


# =====================================================
# INVENTARIOS
# =====================================================

def crear_tabla_ajustes_inventario():

    db_path = get_db_path("inventarios")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS ajustes_inventario (
            id_ajuste INTEGER PRIMARY KEY AUTOINCREMENT,
            folio_ajuste TEXT,
            fecha TEXT,
            codigo_material TEXT,
            descripcion TEXT,
            tipo_ajuste TEXT,
            cantidad REAL,
            stock_anterior REAL,
            stock_nuevo REAL,
            comentarios TEXT,
            usuario TEXT
        )
    """)

    conn.commit()
    conn.close()


# =====================================================
# HOJA CARGA
# =====================================================

def crear_tablas_hoja_carga():

    db_path = get_db_path("inventarios")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS hoja_carga (
            id_hoja_carga INTEGER PRIMARY KEY AUTOINCREMENT,
            folio_hoja_carga TEXT UNIQUE NOT NULL,
            fecha TEXT,
            pedido TEXT,
            cliente TEXT,
            destino TEXT,
            bodega_origen TEXT,
            estatus TEXT,
            responsable_surtido TEXT,
            observaciones TEXT,
            usuario TEXT,
            fecha_creacion TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS detalle_hoja_carga (
            id_detalle_hoja INTEGER PRIMARY KEY AUTOINCREMENT,
            folio_hoja_carga TEXT NOT NULL,
            pedido TEXT,
            codigo_material TEXT,
            descripcion TEXT,
            cantidad_pedido REAL,
            cantidad_surtida REAL,
            bodega TEXT,
            ubicacion TEXT,
            peso REAL DEFAULT 0,
            volumen REAL DEFAULT 0,
            observaciones TEXT
        )
    """)

    conn.commit()
    conn.close()


def alterar_movimientos_inventario():

    db_path = get_db_path("inventarios")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    st.subheader("📋 Estructura actual")

    mostrar_estructura_tabla(
        db_path,
        "movimientos_inventario"
    )

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

            st.success(
                f"✅ Columna agregada: {nombre_columna}"
            )

        except sqlite3.OperationalError:

            st.info(
                f"ℹ️ La columna ya existe: {nombre_columna}"
            )

    conn.commit()
    conn.close()

    st.subheader("📋 Estructura final")

    mostrar_estructura_tabla(
        db_path,
        "movimientos_inventario"
    )


# =====================================================
# LOGISTICA
# =====================================================

def crear_tablas_logistica():

    db_path = get_db_path("logistica")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id_pedido INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido TEXT UNIQUE NOT NULL,
            fecha TEXT,
            cliente TEXT,
            destino TEXT,
            estatus TEXT,
            observaciones TEXT,
            usuario TEXT,
            fecha_creacion TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS detalle_pedido (
            id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido TEXT NOT NULL,
            codigo_material TEXT,
            descripcion TEXT,
            cantidad_pedida REAL,
            peso REAL DEFAULT 0,
            volumen REAL DEFAULT 0,
            bodega TEXT,
            ubicacion TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS embarques (
            id_embarque INTEGER PRIMARY KEY AUTOINCREMENT,
            folio_embarque TEXT UNIQUE NOT NULL,
            pedido TEXT,
            fecha TEXT,
            cliente TEXT,
            destino TEXT,
            transportista TEXT,
            vehiculo TEXT,
            operador TEXT,
            ruta TEXT,
            estatus TEXT,
            observaciones TEXT,
            usuario TEXT,
            fecha_creacion TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS detalle_embarque (
            id_detalle_embarque INTEGER PRIMARY KEY AUTOINCREMENT,
            folio_embarque TEXT NOT NULL,
            pedido TEXT,
            codigo_material TEXT,
            descripcion TEXT,
            cantidad_pedida REAL,
            cantidad_embarcar REAL,
            peso REAL DEFAULT 0,
            volumen REAL DEFAULT 0,
            bodega TEXT,
            ubicacion TEXT
        )
    """)

    conn.commit()
    conn.close()


# =====================================================
# ALTER EMBARQUES
# =====================================================

def alterar_tablas_embarques():

    db_path = get_db_path("logistica")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    st.subheader("📋 Estructura actual embarques")

    mostrar_estructura_tabla(
        db_path,
        "embarques"
    )

    columnas_embarques = [
        ("folio_hoja_carga", "TEXT"),
        ("origen_captura", "TEXT"),
    ]

    st.subheader("🔧 Actualizando tabla embarques")

    for nombre_columna, tipo_columna in columnas_embarques:

        try:

            cur.execute(
                f"""
                ALTER TABLE embarques
                ADD COLUMN {nombre_columna} {tipo_columna}
                """
            )

            st.success(
                f"✅ Columna agregada en embarques: {nombre_columna}"
            )

        except sqlite3.OperationalError:

            st.info(
                f"ℹ️ La columna ya existe en embarques: {nombre_columna}"
            )

    st.subheader("📋 Estructura actual detalle_embarque")

    mostrar_estructura_tabla(
        db_path,
        "detalle_embarque"
    )

    columnas_detalle = [
        ("folio_hoja_carga", "TEXT"),
    ]

    st.subheader("🔧 Actualizando tabla detalle_embarque")

    for nombre_columna, tipo_columna in columnas_detalle:

        try:

            cur.execute(
                f"""
                ALTER TABLE detalle_embarque
                ADD COLUMN {nombre_columna} {tipo_columna}
                """
            )

            st.success(
                f"✅ Columna agregada en detalle_embarque: {nombre_columna}"
            )

        except sqlite3.OperationalError:

            st.info(
                f"ℹ️ La columna ya existe en detalle_embarque: {nombre_columna}"
            )

    conn.commit()
    conn.close()

    st.subheader("📋 Estructura final embarques")

    mostrar_estructura_tabla(
        db_path,
        "embarques"
    )


# =====================================================
# APP
# =====================================================

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
            "Inventarios",
            "Logística"
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
            "movimientos_inventario",
            "inventario_fisico",
            "ajustes_inventario",
            "hoja_carga",
            "detalle_hoja_carga"
        ]

    elif modulo == "Logística":

        tablas_disponibles = [
            "Todas",
            "pedidos",
            "detalle_pedido",
            "embarques",
            "detalle_embarque"
        ]

    tabla = st.selectbox(
        "Selecciona tabla",
        tablas_disponibles,
        key="crear_tablas_tabla"
    )

    # =====================================================
    # CREAR TABLAS
    # =====================================================

    if tipo_proceso == "Crear tabla":

        st.info(
            "Este proceso crea únicamente la tabla seleccionada si no existe."
        )

        if st.button(
            "🚀 Crear tablas",
            key="btn_crear_tablas"
        ):

            try:

                if modulo == "Compras":

                    crear_tablas_compras()

                elif modulo == "Inventarios":

                    if tabla == "Todas":

                        crear_tablas_inventario()

                        crear_tabla_movimientos_inventario()

                        crear_tabla_inventario_fisico()

                        crear_tabla_ajustes_inventario()

                        crear_tablas_hoja_carga()

                    elif tabla == "materiales":

                        crear_tablas_inventario()

                    elif tabla == "movimientos_inventario":

                        crear_tabla_movimientos_inventario()

                    elif tabla == "inventario_fisico":

                        crear_tabla_inventario_fisico()

                    elif tabla == "ajustes_inventario":

                        crear_tabla_ajustes_inventario()

                    elif tabla == "hoja_carga":

                        crear_tablas_hoja_carga()

                    elif tabla == "detalle_hoja_carga":

                        crear_tablas_hoja_carga()

                elif modulo == "Logística":

                    crear_tablas_logistica()

                st.success(
                    f"✅ Tabla(s) creadas correctamente para {modulo}"
                )

            except Exception as e:

                st.error(
                    f"❌ Error creando tablas del módulo {modulo}"
                )

                st.exception(e)

    # =====================================================
    # MODIFICAR ESTRUCTURA
    # =====================================================

    elif tipo_proceso == "Modificar estructura":

        st.warning(
            "Este proceso modifica la estructura de una tabla existente sin borrar datos."
        )

        if (
            modulo == "Inventarios"
            and tabla == "movimientos_inventario"
        ):

            if st.button(
                "🛠️ Modificar estructura",
                key="btn_alter_mov_inv"
            ):

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

        elif (
            
            modulo.lower() == "logística".lower()
            and tabla.lower() == "embarques"
        ):

            if st.button(
                "🛠️ Modificar estructura",
                key="btn_alter_embarques"
            ):

                try:

                    alterar_tablas_embarques()

                    st.success(
                        "✅ Estructura de embarques actualizada"
                    )

                except Exception as e:

                    st.error(
                        "❌ Error modificando embarques"
                    )

                    st.exception(e)

        else:

            st.info(
                "Por ahora la modificación de estructura está habilitada para movimientos_inventario y embarques."
            )
