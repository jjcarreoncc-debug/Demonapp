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

    conn = sqlite3.connect(db_path)

    df = pd.read_sql_query(
        f"PRAGMA table_info({tabla})",
        conn
    )

    conn.close()

    if df.empty:
        st.warning(f"No se encontró estructura para la tabla {tabla}.")
    else:
        st.dataframe(df, use_container_width=True)


def agregar_columna_si_no_existe(cur, tabla, columna, tipo):

    try:

        cur.execute(
            f"""
            ALTER TABLE {tabla}
            ADD COLUMN {columna} {tipo}
            """
        )

        st.success(f"✅ Columna agregada en {tabla}: {columna}")

    except sqlite3.OperationalError as e:

        if "duplicate column name" in str(e).lower():
            st.info(f"ℹ️ La columna ya existe en {tabla}: {columna}")
        else:
            raise e


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

    st.subheader("📋 Estructura actual movimientos_inventario")
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

        agregar_columna_si_no_existe(
            cur,
            "movimientos_inventario",
            nombre_columna,
            tipo_columna
        )

    conn.commit()
    conn.close()

    st.subheader("📋 Estructura final movimientos_inventario")
    mostrar_estructura_tabla(db_path, "movimientos_inventario")


# =====================================================
# LOGISTICA
# =====================================================

def crear_catalogo_estatus_embarque(cur):

    cur.execute("""
        CREATE TABLE IF NOT EXISTS estatus_embarque (
            id_estatus INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_estatus TEXT UNIQUE NOT NULL,
            descripcion TEXT NOT NULL,
            secuencia INTEGER DEFAULT 0,
            activo INTEGER DEFAULT 1,
            fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    estatus_base = [
        ("ALM", "En almacén", 1, 1),
        ("PAT", "En patio", 2, 1),
        ("SAL", "Ya salió", 3, 1),
        ("TRA", "En tránsito", 4, 1),
        ("ENT", "Entregado", 5, 1),
        ("CAN", "Cancelado", 99, 1),
    ]

    cur.executemany("""
        INSERT OR IGNORE INTO estatus_embarque (
            codigo_estatus,
            descripcion,
            secuencia,
            activo
        )
        VALUES (?, ?, ?, ?)
    """, estatus_base)


def crear_tabla_historial_estatus_embarque(cur):

    cur.execute("""
        CREATE TABLE IF NOT EXISTS historial_estatus_embarque (
            id_historial INTEGER PRIMARY KEY AUTOINCREMENT,
            folio_embarque TEXT NOT NULL,
            estatus_anterior TEXT,
            estatus_nuevo TEXT NOT NULL,
            fecha_cambio TEXT DEFAULT CURRENT_TIMESTAMP,
            usuario TEXT,
            observaciones TEXT
        )
    """)


# =====================================================
# EVENTOS EMBARQUE
# =====================================================

def crear_tabla_eventos_embarque(cur):

    cur.execute("""
        CREATE TABLE IF NOT EXISTS eventos_embarque (

            id_evento INTEGER PRIMARY KEY AUTOINCREMENT,

            folio_embarque TEXT NOT NULL,

            fecha_evento TEXT NOT NULL,

            tipo_evento TEXT,

            estatus TEXT,

            ubicacion TEXT,

            comentarios TEXT,

            usuario TEXT,

            latitud REAL DEFAULT 0,

            longitud REAL DEFAULT 0,

            fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP

        )
    """)


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
            folio_hoja_carga TEXT,
            folio_ruta TEXT,
            origen_captura TEXT,
            pedido TEXT,
            fecha TEXT,
            cliente TEXT,
            destino TEXT,
            transportista TEXT,
            vehiculo TEXT,
            placas TEXT,
            operador TEXT,
            ruta TEXT,
            estatus TEXT DEFAULT 'En almacén',
            fecha_estatus TEXT,
            usuario_estatus TEXT,
            observaciones_estatus TEXT,
            observaciones TEXT,
            usuario TEXT,
            fecha_creacion TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS detalle_embarque (
            id_detalle_embarque INTEGER PRIMARY KEY AUTOINCREMENT,
            folio_embarque TEXT NOT NULL,
            folio_hoja_carga TEXT,
            folio_ruta TEXT,
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

    crear_catalogo_estatus_embarque(cur)
    crear_tabla_historial_estatus_embarque(cur)
    crear_tabla_eventos_embarque(cur)

    conn.commit()
    conn.close()


def alterar_tabla_embarques():

    db_path = get_db_path("logistica")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    st.subheader("📋 Estructura actual embarques")
    mostrar_estructura_tabla(db_path, "embarques")

    columnas_embarques = [
        ("folio_hoja_carga", "TEXT"),
        ("folio_ruta", "TEXT"),
        ("origen_captura", "TEXT"),
        ("placas", "TEXT"),
        ("fecha_estatus", "TEXT"),
        ("usuario_estatus", "TEXT"),
        ("observaciones_estatus", "TEXT"),
    ]

    st.subheader("🔧 Actualizando tabla embarques")

    for nombre_columna, tipo_columna in columnas_embarques:

        agregar_columna_si_no_existe(
            cur,
            "embarques",
            nombre_columna,
            tipo_columna
        )

    cur.execute("""
        UPDATE embarques
        SET estatus = 'En almacén'
        WHERE estatus IS NULL OR TRIM(estatus) = ''
    """)

    crear_catalogo_estatus_embarque(cur)
    crear_tabla_historial_estatus_embarque(cur)
    crear_tabla_eventos_embarque(cur)

    conn.commit()
    conn.close()

    st.subheader("📋 Estructura final embarques")
    mostrar_estructura_tabla(db_path, "embarques")

    st.subheader("📋 Catálogo estatus_embarque")
    mostrar_estructura_tabla(db_path, "estatus_embarque")

    st.subheader("📋 Historial estatus embarque")
    mostrar_estructura_tabla(db_path, "historial_estatus_embarque")

    st.subheader("📋 Eventos embarque")
    mostrar_estructura_tabla(db_path, "eventos_embarque")


def alterar_tabla_detalle_embarque():

    db_path = get_db_path("logistica")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    st.subheader("📋 Estructura actual detalle_embarque")
    mostrar_estructura_tabla(db_path, "detalle_embarque")

    columnas_detalle = [
        ("folio_hoja_carga", "TEXT"),
        ("folio_ruta", "TEXT"),
    ]

    st.subheader("🔧 Actualizando tabla detalle_embarque")

    for nombre_columna, tipo_columna in columnas_detalle:

        agregar_columna_si_no_existe(
            cur,
            "detalle_embarque",
            nombre_columna,
            tipo_columna
        )

    conn.commit()
    conn.close()

    st.subheader("📋 Estructura final detalle_embarque")
    mostrar_estructura_tabla(db_path, "detalle_embarque")


def crear_tablas_control_embarques():

    db_path = get_db_path("logistica")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    crear_catalogo_estatus_embarque(cur)
    crear_tabla_historial_estatus_embarque(cur)
    crear_tabla_eventos_embarque(cur)

    conn.commit()
    conn.close()

    st.success("✅ Tablas de control de embarques creadas/actualizadas")

    st.subheader("📋 Catálogo estatus_embarque")
    mostrar_estructura_tabla(db_path, "estatus_embarque")

    st.subheader("📋 Historial estatus_embarque")
    mostrar_estructura_tabla(db_path, "historial_estatus_embarque")

    st.subheader("📋 Eventos embarque")
    mostrar_estructura_tabla(db_path, "eventos_embarque")


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
            "detalle_embarque",
            "estatus_embarque",
            "historial_estatus_embarque",
            "eventos_embarque"
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

                    if tabla == "Todas":

                        crear_tablas_logistica()

                    elif tabla in [
                        "pedidos",
                        "detalle_pedido",
                        "embarques",
                        "detalle_embarque"
                    ]:

                        crear_tablas_logistica()

                    elif tabla in [
                        "estatus_embarque",
                        "historial_estatus_embarque",
                        "eventos_embarque"
                    ]:

                        crear_tablas_control_embarques()

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

        if st.button(
            "🛠️ Modificar estructura",
            key=f"btn_modificar_{modulo}_{tabla}"
        ):

            try:

                if modulo == "Inventarios" and tabla == "movimientos_inventario":

                    alterar_movimientos_inventario()

                elif modulo == "Logística" and tabla == "embarques":

                    alterar_tabla_embarques()

                elif modulo == "Logística" and tabla == "detalle_embarque":

                    alterar_tabla_detalle_embarque()

                elif modulo == "Logística" and tabla == "Todas":

                    alterar_tabla_embarques()
                    alterar_tabla_detalle_embarque()
                    crear_tablas_control_embarques()

                elif modulo == "Logística" and tabla in [
                    "estatus_embarque",
                    "historial_estatus_embarque",
                    "eventos_embarque"
                ]:

                    crear_tablas_control_embarques()

                else:

                    st.warning(
                        f"No hay modificación configurada para: {modulo} / {tabla}"
                    )
                    st.stop()

                st.success(
                    f"✅ Estructura actualizada: {modulo} / {tabla}"
                )

            except Exception as e:

                st.error(
                    f"❌ Error modificando estructura: {modulo} / {tabla}"
                )
                st.exception(e)
