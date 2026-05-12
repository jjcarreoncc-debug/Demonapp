import streamlit as st
import pandas as pd
import sqlite3

from sigem_db import get_db_path


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
    ]
}


DB_POR_TABLA = {

    "materiales": "materiales",

    "movimientos_inventario": "inventarios",

    "entradas_compras": "compras",

    "entradas_compras_detalle": "compras"
}


def carga_tablas_inicial_app():

    st.title("📥 Carga tablas inicial")

    st.caption(
        "Configuración / Carga inicial"
    )

    # =====================================
    # MODULO
    # =====================================

    modulo = st.selectbox(
        "Módulo",
        [
            "Inventarios",
            "Compras"
        ],
        key="carga_modulo"
    )

    # =====================================
    # TABLAS
    # =====================================

    if modulo == "Inventarios":

        tablas_disponibles = [
            "materiales",
            "movimientos_inventario"
        ]

    else:

        tablas_disponibles = [
            "entradas_compras",
            "entradas_compras_detalle"
        ]

    tabla = st.selectbox(
        "Tabla destino",
        tablas_disponibles,
        key="carga_tabla"
    )

    # =====================================
    # ARCHIVO
    # =====================================

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

    # =====================================
    # LEER ARCHIVO
    # =====================================

    try:

        if archivo.name.lower().endswith(".csv"):

            df = pd.read_csv(archivo)

        else:

            df = pd.read_excel(archivo)

    except Exception as e:

        st.error("❌ Error leyendo archivo")
        st.exception(e)

        return

    # =====================================
    # LIMPIAR COLUMNAS
    # =====================================

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    st.success(
        f"✅ Archivo leído correctamente: {len(df)} registros"
    )

    # =====================================
    # PREVIEW
    # =====================================

    st.subheader("👀 Vista previa")

    st.dataframe(
        df.head(20),
        use_container_width=True
    )

    # =====================================
    # VALIDAR COLUMNAS
    # =====================================

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

    # =====================================
    # VALIDAR CODIGOS
    # =====================================

    if "codigo_material" in df.columns:

        if df["codigo_material"].isna().any():

            st.error(
                "❌ Hay registros sin codigo_material"
            )

            return

        duplicados = df[
            df["codigo_material"]
            .duplicated(keep=False)
        ]

        if (
            not duplicados.empty
            and tabla == "materiales"
        ):

            st.warning(
                "⚠️ Hay códigos duplicados en el archivo"
            )

            st.dataframe(
                duplicados,
                use_container_width=True
            )

            return

    # =====================================
    # BASE DESTINO
    # =====================================

    db_nombre = DB_POR_TABLA[tabla]

    db_path = get_db_path(db_nombre)

    st.markdown("---")

    st.write("📂 Base destino:")

    st.code(str(db_path))

    st.write("📋 Tabla destino:")

    st.code(tabla)

    # =====================================
    # CONFIRMAR
    # =====================================

    confirmar = st.checkbox(
        "Confirmo que deseo agregar esta información",
        key="confirmar_carga_inicial"
    )

    if not confirmar:

        st.info(
            "Marca la confirmación para habilitar la carga."
        )

        return

    # =====================================
    # INSERTAR
    # =====================================

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
