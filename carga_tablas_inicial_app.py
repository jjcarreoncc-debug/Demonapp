import streamlit as st
import pandas as pd
import sqlite3

from sigem_db import get_db_path


# =====================================================
# COLUMNAS MINIMAS
# =====================================================

COLUMNAS_MINIMAS = {

    "materiales": [
        "codigo_material",
        "descripcion",
        "categoria",
        "familia",
        "unidad_base",
        "estatus"
    ],

    "movimientos_inventario": [
        "fecha",
        "tipo_movimiento",
        "codigo_material",
        "descripcion",
        "cantidad"
    ],

    "entradas_compras": [
        "proveedor",
        "factura",
        "fecha_factura",
        "fecha_recepcion",
        "moneda"
    ],

    "entradas_compras_detalle": [
        "id_entrada",
        "codigo_material",
        "descripcion",
        "cantidad",
        "costo_unitario"
    ],

    "rutas": [
        "codigo_ruta",
        "descripcion",
        "origen",
        "destino"
    ],

    "puntos_ruta": [
        "codigo_ruta",
        "secuencia",
        "tipo_punto",
        "ubicacion"
    ],

    "transportes": [
        "codigo_transporte",
        "descripcion",
        "tipo_transporte",
        "transportista",
        "vehiculo",
        "placas",
        "operador"
    ],

    "detalle_transporte": [
        "codigo_transporte",
        "folio_embarque",
        "codigo_ruta",
        "fecha_salida",
        "estatus"
    ],

    # =====================================================
    # NUEVO
    # =====================================================

    "embarques": [
        "folio_embarque",
        "pedido",
        "fecha",
        "cliente",
        "destino",
        "transportista",
        "vehiculo",
        "operador",
        "ruta"
    ],

    "detalle_embarque": [
        "folio_embarque",
        "pedido",
        "codigo_material",
        "descripcion",
        "cantidad_pedida",
        "cantidad_embarcar",
        "peso",
        "volumen",
        "bodega"
    ]
}


# =====================================================
# BASES POR TABLA
# =====================================================

DB_POR_TABLA = {

    "materiales": "materiales",

    "movimientos_inventario": "inventarios",

    "entradas_compras": "compras",

    "entradas_compras_detalle": "compras",

    "rutas": "logistica",

    "puntos_ruta": "logistica",

    "transportes": "logistica",

    "detalle_transporte": "logistica",

    # =====================================================
    # NUEVO
    # =====================================================

    "embarques": "logistica",

    "detalle_embarque": "logistica"
}


# =====================================================
# APP
# =====================================================

def carga_tablas_inicial_app():

    st.title("📥 Carga tablas inicial")

    st.caption(
        "Configuración / Carga inicial"
    )

    # =====================================================
    # MODULO
    # =====================================================

    modulo = st.selectbox(
        "Módulo",
        [
            "Inventarios",
            "Compras",
            "Logística"
        ],
        key="carga_modulo"
    )

    # =====================================================
    # TABLAS
    # =====================================================

    if modulo == "Inventarios":

        tablas_disponibles = [
            "materiales",
            "movimientos_inventario"
        ]

    elif modulo == "Compras":

        tablas_disponibles = [
            "entradas_compras",
            "entradas_compras_detalle"
        ]

    elif modulo == "Logística":

        tablas_disponibles = [
            "rutas",
            "puntos_ruta",
            "transportes",
            "detalle_transporte",

            # =====================================================
            # NUEVO
            # =====================================================

            "embarques",
            "detalle_embarque"
        ]

    tabla = st.selectbox(
        "Tabla destino",
        tablas_disponibles,
        key="carga_tabla"
    )

    # =====================================================
    # COLUMNAS REQUERIDAS
    # =====================================================

    st.subheader("📋 Columnas mínimas requeridas")

    st.write(
        COLUMNAS_MINIMAS.get(
            tabla,
            []
        )
    )

    # =====================================================
    # ARCHIVO
    # =====================================================

    archivo = st.file_uploader(
        "Selecciona archivo CSV o Excel",
        type=["csv", "xlsx"],
        key="archivo_carga_inicial"
    )

    if archivo is None:

        st.info(
            "Carga un archivo CSV o Excel para iniciar."
        )

        return

    # =====================================================
    # LEER ARCHIVO
    # =====================================================

    try:

        if archivo.name.lower().endswith(".csv"):

            df = pd.read_csv(archivo)

        else:

            df = pd.read_excel(archivo)

    except Exception as e:

        st.error("❌ Error leyendo archivo")
        st.exception(e)

        return

    # =====================================================
    # LIMPIAR COLUMNAS
    # =====================================================

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    st.success(
        f"✅ Archivo leído correctamente: {len(df)} registros"
    )

    # =====================================================
    # PREVIEW
    # =====================================================

    st.subheader("👀 Vista previa")

    st.dataframe(
        df.head(20),
        use_container_width=True
    )

    # =====================================================
    # VALIDAR COLUMNAS
    # =====================================================

    columnas_minimas = COLUMNAS_MINIMAS.get(
        tabla,
        []
    )

    st.subheader("✅ Validación columnas mínimas")

    columnas_faltantes = [

        col

        for col in columnas_minimas

        if col not in df.columns

    ]

    if columnas_faltantes:

        st.error(
            "❌ Faltan columnas obligatorias"
        )

        st.write(columnas_faltantes)

        st.info(
            "Columnas mínimas requeridas:"
        )

        st.write(columnas_minimas)

        return

    st.success(
        "✅ Columnas mínimas correctas"
    )

    # =====================================================
    # VALIDAR COLUMNAS VS TABLA SQLITE
    # =====================================================

    db_nombre = DB_POR_TABLA[tabla]

    db_path = get_db_path(db_nombre)

    conn_validacion = sqlite3.connect(db_path)

    df_estructura = pd.read_sql_query(
        f"PRAGMA table_info({tabla})",
        conn_validacion
    )

    columnas_tabla = (
        df_estructura["name"]
        .astype(str)
        .str.strip()
        .tolist()
    )

    columnas_invalidas = [

        col

        for col in df.columns

        if col not in columnas_tabla

    ]

    if columnas_invalidas:

        st.error(
            "❌ Existen columnas que no pertenecen a la tabla"
        )

        st.write(columnas_invalidas)

        st.write("📋 Columnas válidas tabla:")

        st.write(columnas_tabla)

        conn_validacion.close()

        return

    conn_validacion.close()

    st.success(
        "✅ Validación estructura tabla correcta"
    )

    # =====================================================
    # VALIDACIONES ESPECIALES
    # =====================================================

    if tabla == "rutas":

        if df["codigo_ruta"].isna().any():

            st.error(
                "❌ Hay registros sin codigo_ruta"
            )

            return

    if tabla == "transportes":

        if df["codigo_transporte"].isna().any():

            st.error(
                "❌ Hay registros sin codigo_transporte"
            )

            return

    if tabla == "detalle_transporte":

        if df["codigo_transporte"].isna().any():

            st.error(
                "❌ Hay registros sin codigo_transporte"
            )

            return

    if tabla == "embarques":

        if df["folio_embarque"].isna().any():

            st.error(
                "❌ Hay registros sin folio_embarque"
            )

            return

    if tabla == "detalle_embarque":

        if df["folio_embarque"].isna().any():

            st.error(
                "❌ Hay registros sin folio_embarque"
            )

            return

    # =====================================================
    # BASE DESTINO
    # =====================================================

    st.markdown("---")

    st.write("📂 Base destino:")

    st.code(str(db_path))

    st.write("📋 Tabla destino:")

    st.code(tabla)

    # =====================================================
    # CONFIRMAR
    # =====================================================

    confirmar = st.checkbox(
        "Confirmo que deseo agregar esta información",
        key="confirmar_carga_inicial"
    )

    if not confirmar:

        st.info(
            "Marca la confirmación para habilitar la carga."
        )

        return

    # =====================================================
    # INSERTAR
    # =====================================================

    if st.button(
        "🚀 Ejecutar carga",
        key="btn_ejecutar_carga_inicial"
    ):

        try:

            conn = sqlite3.connect(db_path)

            df.to_sql(
                tabla,
                conn,
                if_exists="append",
                index=False
            )

            total = pd.read_sql_query(
                f"""
                SELECT COUNT(*) AS total
                FROM {tabla}
                """,
                conn
            )["total"].iloc[0]

            conn.close()

            st.success(
                "✅ Información cargada correctamente"
            )

            st.write(
                "📊 Registros cargados desde archivo:"
            )

            st.write(len(df))

            st.write(
                "📦 Total registros actuales en tabla:"
            )

            st.write(total)

        except Exception as e:

            st.error(
                "❌ Error cargando información"
            )

            st.exception(e)


if __name__ == "__main__":

    carga_tablas_inicial_app()
