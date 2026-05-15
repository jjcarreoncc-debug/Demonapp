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

from seguridad_db import crear_tablas_seguridad


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


def normalizar_texto(texto):

    return str(texto).strip().lower().replace("í", "i")


def obtener_db_por_modulo(modulo):

    modulo_limpio = normalizar_texto(modulo)

    if modulo_limpio == "compras":
        return "compras"

    if modulo_limpio == "inventarios":
        return "inventarios"

    if modulo_limpio == "logistica":
        return "logistica"

    if modulo_limpio == "seguridad":
        return "erp"

    return None


def borrar_tabla(modulo, tabla):

    db_nombre = obtener_db_por_modulo(modulo)

    if db_nombre is None:
        raise Exception(
            "No se encontró base de datos para el módulo seleccionado."
        )

    db_path = get_db_path(db_nombre)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute(
        f"DROP TABLE IF EXISTS {tabla}"
    )

    conn.commit()
    conn.close()

    return db_path


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
            prioridad TEXT,
            ruta_sugerida TEXT,
            estatus_hoja_carga TEXT,
            peso_total REAL DEFAULT 0,
            volumen_total REAL DEFAULT 0,
            transportista_sugerido TEXT,
            tipo_transporte TEXT,
            fecha_entrega TEXT,
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


def alterar_tabla_hoja_carga():

    db_path = get_db_path("inventarios")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    st.subheader("📋 Estructura actual hoja_carga")
    mostrar_estructura_tabla(db_path, "hoja_carga")

    columnas_hoja = [
        ("prioridad", "TEXT"),
        ("ruta_sugerida", "TEXT"),
        ("estatus_hoja_carga", "TEXT"),
        ("peso_total", "REAL DEFAULT 0"),
        ("volumen_total", "REAL DEFAULT 0"),
        ("transportista_sugerido", "TEXT"),
        ("tipo_transporte", "TEXT"),
        ("fecha_entrega", "TEXT"),
        ("bodega_origen", "TEXT"),
        ("estatus", "TEXT"),
        ("responsable_surtido", "TEXT"),
        ("observaciones", "TEXT"),
        ("usuario", "TEXT"),
        ("fecha_creacion", "TEXT")
    ]

    st.subheader("🔧 Actualizando tabla hoja_carga")

    for nombre_columna, tipo_columna in columnas_hoja:

        agregar_columna_si_no_existe(
            cur,
            "hoja_carga",
            nombre_columna,
            tipo_columna
        )

    conn.commit()
    conn.close()

    st.subheader("📋 Estructura final hoja_carga")
    mostrar_estructura_tabla(db_path, "hoja_carga")


def alterar_tabla_detalle_hoja_carga():

    db_path = get_db_path("inventarios")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    st.subheader("📋 Estructura actual detalle_hoja_carga")
    mostrar_estructura_tabla(db_path, "detalle_hoja_carga")

    columnas_detalle = [
        ("pedido", "TEXT"),
        ("codigo_material", "TEXT"),
        ("descripcion", "TEXT"),
        ("cantidad_pedido", "REAL"),
        ("cantidad_surtida", "REAL"),
        ("bodega", "TEXT"),
        ("ubicacion", "TEXT"),
        ("peso", "REAL DEFAULT 0"),
        ("volumen", "REAL DEFAULT 0"),
        ("observaciones", "TEXT")
    ]

    st.subheader("🔧 Actualizando tabla detalle_hoja_carga")

    for nombre_columna, tipo_columna in columnas_detalle:

        agregar_columna_si_no_existe(
            cur,
            "detalle_hoja_carga",
            nombre_columna,
            tipo_columna
        )

    conn.commit()
    conn.close()

    st.subheader("📋 Estructura final detalle_hoja_carga")
    mostrar_estructura_tabla(db_path, "detalle_hoja_carga")


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
        ("PEN", "Pendiente", 0, 1),
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


def crear_tabla_eventos_embarque(cur):

    cur.execute("""
        CREATE TABLE IF NOT EXISTS eventos_embarque (
            id_evento INTEGER PRIMARY KEY AUTOINCREMENT,
            folio_embarque TEXT NOT NULL,
            codigo_transporte TEXT,
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


def crear_tabla_rutas(cur):

    cur.execute("""
        CREATE TABLE IF NOT EXISTS rutas (
            id_ruta INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_ruta TEXT UNIQUE NOT NULL,
            descripcion TEXT,
            origen TEXT,
            destino TEXT,
            distancia_km REAL DEFAULT 0,
            tiempo_estimado REAL DEFAULT 0,
            activo INTEGER DEFAULT 1,
            usuario TEXT,
            fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)


def crear_tabla_puntos_ruta(cur):

    cur.execute("""
        CREATE TABLE IF NOT EXISTS puntos_ruta (
            id_punto INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_ruta TEXT NOT NULL,
            secuencia INTEGER DEFAULT 0,
            tipo_punto TEXT,
            ubicacion TEXT,
            ciudad TEXT,
            estado TEXT,
            latitud REAL DEFAULT 0,
            longitud REAL DEFAULT 0,
            tiempo_estimado REAL DEFAULT 0,
            activo INTEGER DEFAULT 1,
            usuario TEXT,
            fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)


def crear_tabla_transportes(cur):

    cur.execute("""
        CREATE TABLE IF NOT EXISTS transportes (
            id_transporte INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_transporte TEXT UNIQUE NOT NULL,
            descripcion TEXT,
            tipo_transporte TEXT,
            transportista TEXT,
            vehiculo TEXT,
            placas TEXT,
            operador TEXT,
            telefono_operador TEXT,
            codigo_ruta TEXT,
            capacidad_peso REAL DEFAULT 0,
            capacidad_volumen REAL DEFAULT 0,
            estatus TEXT DEFAULT 'Disponible',
            activo INTEGER DEFAULT 1,
            observaciones TEXT,
            usuario TEXT,
            fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)


def crear_tabla_detalle_transporte(cur):

    cur.execute("""
        CREATE TABLE IF NOT EXISTS detalle_transporte (
            id_detalle_transporte INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_transporte TEXT NOT NULL,
            folio_embarque TEXT,
            folio_hoja_carga TEXT,
            pedido TEXT,
            codigo_ruta TEXT,
            fecha_salida TEXT,
            fecha_llegada TEXT,
            operador TEXT,
            ayudante TEXT,
            kilometraje_salida REAL DEFAULT 0,
            kilometraje_llegada REAL DEFAULT 0,
            combustible REAL DEFAULT 0,
            casetas REAL DEFAULT 0,
            viaticos REAL DEFAULT 0,
            estatus TEXT DEFAULT 'Activo',
            observaciones TEXT,
            usuario TEXT,
            fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)


def crear_tabla_incidencias(cur):

    cur.execute("""
        CREATE TABLE IF NOT EXISTS incidencias (
            id_incidencia INTEGER PRIMARY KEY AUTOINCREMENT,
            folio_incidencia TEXT UNIQUE NOT NULL,
            fecha TEXT,
            modulo TEXT DEFAULT 'Logística',
            proceso TEXT,
            tipo_incidencia TEXT,
            prioridad TEXT DEFAULT 'Media',
            estatus TEXT DEFAULT 'Abierta',
            folio_referencia TEXT,
            folio_embarque TEXT,
            folio_hoja_carga TEXT,
            pedido TEXT,
            codigo_material TEXT,
            descripcion TEXT,
            cantidad REAL DEFAULT 0,
            cliente TEXT,
            destino TEXT,
            bodega TEXT,
            ubicacion TEXT,
            transportista TEXT,
            vehiculo TEXT,
            placas TEXT,
            operador TEXT,
            responsable TEXT,
            descripcion_incidencia TEXT,
            causa TEXT,
            solucion TEXT,
            fecha_solucion TEXT,
            usuario_registro TEXT,
            usuario_cierre TEXT,
            observaciones TEXT,
            fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)


def crear_tablas_incidencias_logistica():

    db_path = get_db_path("logistica")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    crear_tabla_incidencias(cur)

    conn.commit()
    conn.close()

    st.success("✅ Tabla incidencias creada o actualizada")

    st.subheader("📋 Incidencias")
    mostrar_estructura_tabla(db_path, "incidencias")


def crear_tablas_rutas_logistica():

    db_path = get_db_path("logistica")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    crear_tabla_rutas(cur)
    crear_tabla_puntos_ruta(cur)
    crear_tabla_transportes(cur)
    crear_tabla_detalle_transporte(cur)

    conn.commit()
    conn.close()

    st.success("✅ Tablas de rutas / transportes creadas o actualizadas")

    st.subheader("📋 Rutas")
    mostrar_estructura_tabla(db_path, "rutas")

    st.subheader("📋 Puntos ruta")
    mostrar_estructura_tabla(db_path, "puntos_ruta")

    st.subheader("📋 Transportes")
    mostrar_estructura_tabla(db_path, "transportes")

    st.subheader("📋 Detalle transporte")
    mostrar_estructura_tabla(db_path, "detalle_transporte")


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
    crear_tabla_rutas(cur)
    crear_tabla_puntos_ruta(cur)
    crear_tabla_transportes(cur)
    crear_tabla_detalle_transporte(cur)
    crear_tabla_incidencias(cur)

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
        ("codigo_transporte", "TEXT"),
        ("codigo_ruta", "TEXT"),
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
    crear_tabla_rutas(cur)
    crear_tabla_puntos_ruta(cur)
    crear_tabla_transportes(cur)
    crear_tabla_detalle_transporte(cur)
    crear_tabla_incidencias(cur)

    conn.commit()
    conn.close()

    st.subheader("📋 Estructura final embarques")
    mostrar_estructura_tabla(db_path, "embarques")


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


def alterar_tabla_incidencias():

    db_path = get_db_path("logistica")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    st.subheader("📋 Estructura actual incidencias")
    mostrar_estructura_tabla(db_path, "incidencias")

    crear_tabla_incidencias(cur)

    conn.commit()
    conn.close()

    st.subheader("📋 Estructura final incidencias")
    mostrar_estructura_tabla(db_path, "incidencias")


def crear_tablas_control_embarques():

    db_path = get_db_path("logistica")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    crear_catalogo_estatus_embarque(cur)
    crear_tabla_historial_estatus_embarque(cur)
    crear_tabla_eventos_embarque(cur)
    crear_tabla_rutas(cur)
    crear_tabla_puntos_ruta(cur)
    crear_tabla_transportes(cur)
    crear_tabla_detalle_transporte(cur)
    crear_tabla_incidencias(cur)

    conn.commit()
    conn.close()

    st.success("✅ Tablas de control de embarques creadas/actualizadas")


def crear_tablas_seguridad_app():

    crear_tablas_seguridad()

    db_path = get_db_path("erp")

    st.success("✅ Tablas de seguridad creadas/actualizadas")

    tablas = [
        "usuarios",
        "roles",
        "permisos",
        "modulos",
        "usuario_roles",
        "rol_permisos",
        "sesiones_usuario"
    ]

    for tabla in tablas:

        st.subheader(f"📋 {tabla}")
        mostrar_estructura_tabla(db_path, tabla)


# =====================================================
# APP
# =====================================================

def crear_tablas_app():

    st.title("🗄️ Crear / modificar / borrar tablas")

    tipo_proceso = st.selectbox(
        "Tipo proceso",
        [
            "Crear tabla",
            "Modificar estructura",
            "Borrar tabla"
        ],
        key="tipo_proceso_tablas"
    )

    modulo = st.selectbox(
        "Selecciona módulo",
        [
            "Compras",
            "Inventarios",
            "Logística",
            "Seguridad"
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
            "eventos_embarque",
            "rutas",
            "puntos_ruta",
            "transportes",
            "detalle_transporte",
            "incidencias"
        ]

    elif modulo == "Seguridad":

        tablas_disponibles = [
            "Todas",
            "usuarios",
            "roles",
            "permisos",
            "modulos",
            "usuario_roles",
            "rol_permisos",
            "sesiones_usuario"
        ]

    tabla = st.selectbox(
        "Selecciona tabla",
        tablas_disponibles,
        key="crear_tablas_tabla"
    )

    tabla_limpia = normalizar_texto(tabla)
    modulo_limpio = normalizar_texto(modulo)

    if tipo_proceso == "Crear tabla":

        st.info(
            "Este proceso crea únicamente la tabla seleccionada si no existe."
        )

        if st.button(
            "🚀 Crear tablas",
            key="btn_crear_tablas"
        ):

            try:

                if modulo_limpio == "seguridad":

                    crear_tablas_seguridad_app()

                elif modulo_limpio == "compras":

                    crear_tablas_compras()

                elif modulo_limpio == "inventarios":

                    if tabla_limpia == "todas":

                        crear_tablas_inventario()
                        crear_tabla_movimientos_inventario()
                        crear_tabla_inventario_fisico()
                        crear_tabla_ajustes_inventario()
                        crear_tablas_hoja_carga()

                    elif tabla_limpia == "materiales":

                        crear_tablas_inventario()

                    elif tabla_limpia == "movimientos_inventario":

                        crear_tabla_movimientos_inventario()

                    elif tabla_limpia == "inventario_fisico":

                        crear_tabla_inventario_fisico()

                    elif tabla_limpia == "ajustes_inventario":

                        crear_tabla_ajustes_inventario()

                    elif tabla_limpia == "hoja_carga":

                        crear_tablas_hoja_carga()

                    elif tabla_limpia == "detalle_hoja_carga":

                        crear_tablas_hoja_carga()

                elif modulo_limpio == "logistica":

                    if tabla_limpia == "todas":

                        crear_tablas_logistica()

                    elif tabla_limpia in [
                        "pedidos",
                        "detalle_pedido",
                        "embarques",
                        "detalle_embarque"
                    ]:

                        crear_tablas_logistica()

                    elif tabla_limpia in [
                        "estatus_embarque",
                        "historial_estatus_embarque",
                        "eventos_embarque"
                    ]:

                        crear_tablas_control_embarques()

                    elif tabla_limpia in [
                        "rutas",
                        "puntos_ruta",
                        "transportes",
                        "detalle_transporte"
                    ]:

                        crear_tablas_rutas_logistica()

                    elif tabla_limpia == "incidencias":

                        crear_tablas_incidencias_logistica()

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

        if st.button(
            "🛠️ Modificar estructura",
            key=f"btn_modificar_{modulo_limpio}_{tabla_limpia}"
        ):

            try:

                st.info(f"Validando modificación: {modulo_limpio} / {tabla_limpia}")

                if modulo_limpio == "seguridad":

                    crear_tablas_seguridad_app()

                elif modulo_limpio == "inventarios" and tabla_limpia == "hoja_carga":

                    alterar_tabla_hoja_carga()

                elif modulo_limpio == "inventarios" and tabla_limpia == "detalle_hoja_carga":

                    alterar_tabla_detalle_hoja_carga()

                elif modulo_limpio == "inventarios" and tabla_limpia == "movimientos_inventario":

                    alterar_movimientos_inventario()

                elif modulo_limpio == "inventarios" and tabla_limpia == "todas":

                    alterar_tabla_hoja_carga()
                    alterar_tabla_detalle_hoja_carga()
                    alterar_movimientos_inventario()

                elif modulo_limpio == "logistica" and tabla_limpia == "embarques":

                    alterar_tabla_embarques()

                elif modulo_limpio == "logistica" and tabla_limpia == "detalle_embarque":

                    alterar_tabla_detalle_embarque()

                elif modulo_limpio == "logistica" and tabla_limpia == "incidencias":

                    alterar_tabla_incidencias()

                elif modulo_limpio == "logistica" and tabla_limpia == "todas":

                    alterar_tabla_embarques()
                    alterar_tabla_detalle_embarque()
                    alterar_tabla_incidencias()
                    crear_tablas_control_embarques()
                    crear_tablas_rutas_logistica()

                elif modulo_limpio == "logistica" and tabla_limpia in [
                    "estatus_embarque",
                    "historial_estatus_embarque",
                    "eventos_embarque"
                ]:

                    crear_tablas_control_embarques()

                elif modulo_limpio == "logistica" and tabla_limpia in [
                    "rutas",
                    "puntos_ruta",
                    "transportes",
                    "detalle_transporte"
                ]:

                    crear_tablas_rutas_logistica()

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

    elif tipo_proceso == "Borrar tabla":

        st.error(
            "⚠️ Este proceso elimina completamente la tabla y toda su información."
        )

        st.warning(
            "⚠️ Esta acción no se puede deshacer."
        )

        if tabla_limpia == "todas":

            st.error(
                "Por seguridad no se permite borrar 'Todas'. Selecciona una tabla específica."
            )
            st.stop()

        confirmar_borrado = st.checkbox(
            f"Confirmo borrar la tabla: {tabla}",
            key=f"confirmar_borrado_{modulo_limpio}_{tabla_limpia}"
        )

        if not confirmar_borrado:

            st.info(
                "Marca la confirmación para habilitar el borrado."
            )
            st.stop()

        if st.button(
            "🗑️ Borrar tabla",
            key=f"btn_borrar_{modulo_limpio}_{tabla_limpia}"
        ):

            try:

                db_path = borrar_tabla(
                    modulo,
                    tabla
                )

                st.success(
                    f"✅ Tabla eliminada correctamente: {tabla}"
                )

                st.write("📂 Base afectada:")
                st.code(str(db_path))

            except Exception as e:

                st.error(
                    f"❌ Error borrando tabla: {tabla}"
                )
                st.exception(e)
