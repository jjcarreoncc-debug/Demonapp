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

    "hoja_carga": [
        "folio_hoja_carga",
        "fecha",
        "pedido",
        "cliente",
        "destino",
        "bodega_origen",
        "estatus",
        "responsable_surtido"
    ],

    "detalle_hoja_carga": [
        "folio_hoja_carga",
        "pedido",
        "codigo_material",
        "descripcion",
        "cantidad_pedido",
        "cantidad_surtida",
        "bodega",
        "ubicacion",
        "peso",
        "volumen"
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
    #

        "pedidos": [
        "pedido",
        "fecha",
        "cliente",
        "destino",
        "estatus"
    ],

    "detalle_pedido": [
        "pedido",
        "codigo_material",
        "descripcion",
        "cantidad_pedida",
        "bodega",
        "ubicacion",
        "peso",
        "volumen"
    ],
    #
    "rutas": [
        "codigo_ruta",
        "descripcion",
        "origen",
        "destino"
    ],
    #
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
    ],

    "incidencias": [
        "folio_incidencia",
        "fecha",
        "modulo",
        "proceso",
        "tipo_incidencia",
        "prioridad",
        "estatus",
        "folio_referencia",
        "folio_embarque",
        "folio_hoja_carga",
        "pedido",
        "codigo_material",
        "descripcion",
        "cantidad",
        "cliente",
        "destino",
        "bodega",
        "ubicacion",
        "transportista",
        "vehiculo",
        "placas",
        "operador",
        "responsable",
        "descripcion_incidencia",
        "causa",
        "solucion",
        "fecha_solucion",
        "usuario_registro",
        "usuario_cierre",
        "observaciones",
        "fecha_creacion"
    ],

    "roles": [
        "nombre_rol",
        "descripcion",
        "estatus",
        "estado"
    ],

    "modulos": [
        "nombre_modulo",
        "ruta",
        "icono",
        "orden_menu",
        "activo",
        "estado"
    ],

    "usuario_roles": [
        "id_usuario",
        "id_rol"
    ],

    "rol_permisos": [
        "id_rol",
        "id_modulo",
        "puede_ver",
        "puede_crear",
        "puede_editar",
        "puede_borrar"
    ]
}


# =====================================================
# BASES POR TABLA
# =====================================================

DB_POR_TABLA = {

    "materiales": "materiales",

    "movimientos_inventario": "inventarios",

    "hoja_carga": "inventarios",

    "detalle_hoja_carga": "inventarios",

    "entradas_compras": "compras",

    "entradas_compras_detalle": "compras",

    "pedidos": "logistica",

    "detalle_pedido": "logistica",

    "rutas": "logistica",

    "puntos_ruta": "logistica",

    "transportes": "logistica",

    "detalle_transporte": "logistica",

    "embarques": "logistica",

    "detalle_embarque": "logistica",

    "incidencias": "logistica",

    "roles": "seguridad",

    "modulos": "seguridad",

    "usuario_roles": "seguridad",

    "rol_permisos": "seguridad"
}


# =====================================================
# CAMPOS NUEVOS MATERIALES
# =====================================================

CAMPOS_LOGISTICOS_MATERIALES = {

    "tipo_manejo": "TEXT",
    "unidad_logistica": "TEXT",

    "piezas_por_caja": "REAL",
    "cajas_por_tarima": "REAL",
    "piezas_por_tarima": "REAL",

    "peso_unitario": "REAL",
    "volumen_unitario": "REAL",

    "largo": "REAL",
    "ancho": "REAL",
    "alto": "REAL",

    "requiere_tarima": "TEXT",
    "requiere_lote": "TEXT",
    "requiere_serie": "TEXT",
    "control_caducidad": "TEXT",

    "codigo_barras": "TEXT",
    "codigo_qr": "TEXT",

    "observaciones_logisticas": "TEXT"
}


# =====================================================
# UTILIDADES ALTER TABLE
# =====================================================

def obtener_columnas_tabla(conn, tabla):

    try:

        df_cols = pd.read_sql_query(
            f"PRAGMA table_info({tabla})",
            conn
        )

        return df_cols["name"].tolist()

    except Exception:

        return []


def agregar_columna_si_no_existe(
    conn,
    tabla,
    columna,
    tipo_dato
):

    columnas_actuales = obtener_columnas_tabla(
        conn,
        tabla
    )

    if columna in columnas_actuales:

        return "YA_EXISTE"

    cursor = conn.cursor()

    cursor.execute(
        f"""
        ALTER TABLE {tabla}
        ADD COLUMN {columna} {tipo_dato}
        """
    )

    return "AGREGADA"


def alterar_tabla_materiales_logistica():

    db_path = get_db_path("materiales")

    conn = sqlite3.connect(db_path)

    resultados = []

    try:

        for columna, tipo_dato in CAMPOS_LOGISTICOS_MATERIALES.items():

            resultado = agregar_columna_si_no_existe(
                conn,
                "materiales",
                columna,
                tipo_dato
            )

            resultados.append(
                {
                    "campo": columna,
                    "tipo": tipo_dato,
                    "resultado": resultado
                }
            )

        conn.commit()

    except Exception as e:

        conn.rollback()
        conn.close()

        raise e

    conn.close()

    return pd.DataFrame(resultados)


def mostrar_estructura_tabla(
    db_nombre,
    tabla
):

    db_path = get_db_path(db_nombre)

    conn = sqlite3.connect(db_path)

    df = pd.read_sql_query(
        f"PRAGMA table_info({tabla})",
        conn
    )

    conn.close()

    return df


# =====================================================
# APP
# =====================================================

def carga_tablas_inicial_app():

    st.title("📥 Carga tablas inicial")

    st.caption(
        "⚙️ Configuración / Carga inicial"
    )

    modulo = st.selectbox(
        "Módulo",
        [
            "Inventarios",
            "Compras",
            "Logística",
            "Seguridad"
        ],
        key="carga_modulo"
    )

    if modulo == "Inventarios":

        tablas_disponibles = [
            "materiales",
            "movimientos_inventario",
            "hoja_carga",
            "detalle_hoja_carga"
        ]

    elif modulo == "Compras":

        tablas_disponibles = [
            "entradas_compras",
            "entradas_compras_detalle"
        ]

    elif modulo == "Logística":
        #
        tablas_disponibles = [

            "clientes",
        
            "pedidos",
        
            "detalle_pedido",
        
            "rutas",
        
            "puntos_ruta",
        
            "transportes",
        
            "detalle_transporte",
        
            "embarques",
        
            "detalle_embarque",
        
            "incidencias"
        ]
        #
    elif modulo == "Seguridad":

        tablas_disponibles = [
            "roles",
            "modulos",
            "usuario_roles",
            "rol_permisos"
        ]

    tabla = st.selectbox(
        "Tabla destino",
        tablas_disponibles,
        key="carga_tabla"
    )

    # =====================================================
    # MODIFICAR ESTRUCTURA MATERIALES
    # =====================================================

    if modulo == "Inventarios" and tabla == "materiales":

        st.markdown("---")

        st.subheader("🛠️ Estructura logística de materiales")

        st.info(
            "Este proceso agrega campos logísticos a la tabla materiales sin borrar información existente."
        )

        with st.expander("👀 Campos que se agregarán"):

            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "campo": campo,
                            "tipo": tipo
                        }
                        for campo, tipo in CAMPOS_LOGISTICOS_MATERIALES.items()
                    ]
                ),
                use_container_width=True,
                hide_index=True
            )

        if st.button(
            "🛠️ Modificar estructura materiales",
            key="btn_alter_materiales_logistica"
        ):

            try:

                resultado_alter = alterar_tabla_materiales_logistica()

                st.success(
                    "✅ Estructura de materiales actualizada correctamente."
                )

                st.dataframe(
                    resultado_alter,
                    use_container_width=True,
                    hide_index=True
                )

            except Exception as e:

                st.error(
                    "❌ Error modificando estructura de materiales."
                )

                st.exception(e)

        with st.expander("📋 Ver estructura actual de materiales"):

            try:

                estructura = mostrar_estructura_tabla(
                    "materiales",
                    "materiales"
                )

                st.dataframe(
                    estructura,
                    use_container_width=True,
                    hide_index=True
                )

            except Exception as e:

                st.error(
                    "❌ Error leyendo estructura de materiales."
                )

                st.exception(e)

    st.markdown("---")

    st.subheader("📋 Columnas mínimas requeridas")

    st.write(
        COLUMNAS_MINIMAS.get(
            tabla,
            []
        )
    )

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

    try:

        if archivo.name.lower().endswith(".csv"):

            df = pd.read_csv(archivo)

        else:

            df = pd.read_excel(archivo)

    except Exception as e:

        st.error("❌ Error leyendo archivo")
        st.exception(e)

        return

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    st.success(
        f"✅ Archivo leído correctamente: {len(df)} registros"
    )

    st.subheader("👀 Vista previa")

    st.dataframe(
        df.head(20),
        use_container_width=True
    )

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
    # VALIDACIONES ESPECIALES INVENTARIOS
    # =====================================================

    if tabla == "hoja_carga":

        if df["folio_hoja_carga"].isna().any():

            st.error(
                "❌ Hay registros sin folio_hoja_carga"
            )

            return

        if df["cliente"].isna().any():

            st.error(
                "❌ Hay registros sin cliente"
            )

            return

        if df["destino"].isna().any():

            st.error(
                "❌ Hay registros sin destino"
            )

            return

        duplicados = df[
            df["folio_hoja_carga"]
            .duplicated(keep=False)
        ]

        if not duplicados.empty:

            st.warning(
                "⚠️ Hay folio_hoja_carga duplicados en el archivo"
            )

            st.dataframe(
                duplicados,
                use_container_width=True
            )

            return

    if tabla == "detalle_hoja_carga":

        if df["folio_hoja_carga"].isna().any():

            st.error(
                "❌ Hay registros sin folio_hoja_carga"
            )

            return

        if df["codigo_material"].isna().any():

            st.error(
                "❌ Hay registros sin codigo_material"
            )

            return

        if df["cantidad_pedido"].isna().any():

            st.error(
                "❌ Hay registros sin cantidad_pedido"
            )

            return

    # =====================================================
    # VALIDACIONES ESPECIALES LOGISTICA
    # =====================================================

    if tabla == "rutas":

        if df["codigo_ruta"].isna().any():

            st.error(
                "❌ Hay registros sin codigo_ruta"
            )

            return

        duplicados = df[
            df["codigo_ruta"]
            .duplicated(keep=False)
        ]

        if not duplicados.empty:

            st.warning(
                "⚠️ Hay codigo_ruta duplicados"
            )

            st.dataframe(
                duplicados,
                use_container_width=True
            )

            return

    if tabla == "puntos_ruta":

        if df["codigo_ruta"].isna().any():

            st.error(
                "❌ Hay registros sin codigo_ruta"
            )

            return

        if df["secuencia"].isna().any():

            st.error(
                "❌ Hay registros sin secuencia"
            )

            return

    if tabla == "transportes":

        if df["codigo_transporte"].isna().any():

            st.error(
                "❌ Hay registros sin codigo_transporte"
            )

            return

        duplicados = df[
            df["codigo_transporte"]
            .duplicated(keep=False)
        ]

        if not duplicados.empty:

            st.warning(
                "⚠️ Hay codigo_transporte duplicados"
            )

            st.dataframe(
                duplicados,
                use_container_width=True
            )

            return

    if tabla == "detalle_transporte":

        if df["codigo_transporte"].isna().any():

            st.error(
                "❌ Hay registros sin codigo_transporte"
            )

            return

        if df["folio_embarque"].isna().any():

            st.error(
                "❌ Hay registros sin folio_embarque"
            )

            return

        if df["codigo_ruta"].isna().any():

            st.error(
                "❌ Hay registros sin codigo_ruta"
            )

            return

    if tabla == "embarques":

        if df["folio_embarque"].isna().any():

            st.error(
                "❌ Hay registros sin folio_embarque"
            )

            return

        duplicados = df[
            df["folio_embarque"]
            .duplicated(keep=False)
        ]

        if not duplicados.empty:

            st.warning(
                "⚠️ Hay folio_embarque duplicados"
            )

            st.dataframe(
                duplicados,
                use_container_width=True
            )

            return

    if tabla == "detalle_embarque":

        if df["folio_embarque"].isna().any():

            st.error(
                "❌ Hay registros sin folio_embarque"
            )

            return

        if df["codigo_material"].isna().any():

            st.error(
                "❌ Hay registros sin codigo_material"
            )

            return

    if tabla == "incidencias":

        if df["folio_incidencia"].isna().any():

            st.error(
                "❌ Hay registros sin folio_incidencia"
            )

            return

        if df["fecha"].isna().any():

            st.error(
                "❌ Hay registros sin fecha"
            )

            return

        if df["tipo_incidencia"].isna().any():

            st.error(
                "❌ Hay registros sin tipo_incidencia"
            )

            return

        if df["prioridad"].isna().any():

            st.error(
                "❌ Hay registros sin prioridad"
            )

            return

        if df["estatus"].isna().any():

            st.error(
                "❌ Hay registros sin estatus"
            )

            return

        if df["descripcion_incidencia"].isna().any():

            st.error(
                "❌ Hay registros sin descripcion_incidencia"
            )

            return

        duplicados = df[
            df["folio_incidencia"]
            .duplicated(keep=False)
        ]

        if not duplicados.empty:

            st.warning(
                "⚠️ Hay folio_incidencia duplicados"
            )

            st.dataframe(
                duplicados,
                use_container_width=True
            )

            return

    # =====================================================
    # VALIDACIONES ESPECIALES SEGURIDAD
    # =====================================================

    if tabla == "roles":

        if df["nombre_rol"].isna().any():

            st.error(
                "❌ Hay registros sin nombre_rol"
            )

            return

        duplicados = df[
            df["nombre_rol"]
            .astype(str)
            .str.strip()
            .str.lower()
            .duplicated(keep=False)
        ]

        if not duplicados.empty:

            st.warning(
                "⚠️ Hay nombre_rol duplicados en el archivo"
            )

            st.dataframe(
                df[duplicados],
                use_container_width=True
            )

            return

    if tabla == "modulos":

        if df["nombre_modulo"].isna().any():

            st.error(
                "❌ Hay registros sin nombre_modulo"
            )

            return

        if df["ruta"].isna().any():

            st.error(
                "❌ Hay registros sin ruta"
            )

            return

        if df["orden_menu"].isna().any():

            st.error(
                "❌ Hay registros sin orden_menu"
            )

            return

        duplicados = df[
            df["ruta"]
            .astype(str)
            .str.strip()
            .str.lower()
            .duplicated(keep=False)
        ]

        if not duplicados.empty:

            st.warning(
                "⚠️ Hay rutas duplicadas en el archivo"
            )

            st.dataframe(
                df[duplicados],
                use_container_width=True
            )

            return

    if tabla == "usuario_roles":

        if df["id_usuario"].isna().any():

            st.error(
                "❌ Hay registros sin id_usuario"
            )

            return

        if df["id_rol"].isna().any():

            st.error(
                "❌ Hay registros sin id_rol"
            )

            return

        duplicados = df[
            ["id_usuario", "id_rol"]
        ].duplicated(keep=False)

        if not duplicados.empty:

            st.warning(
                "⚠️ Hay asignaciones usuario/rol duplicadas en el archivo"
            )

            st.dataframe(
                df[duplicados],
                use_container_width=True
            )

            return

    if tabla == "rol_permisos":

        if df["id_rol"].isna().any():

            st.error(
                "❌ Hay registros sin id_rol"
            )

            return

        if df["id_modulo"].isna().any():

            st.error(
                "❌ Hay registros sin id_modulo"
            )

            return

        columnas_permiso = [
            "puede_ver",
            "puede_crear",
            "puede_editar",
            "puede_borrar"
        ]

        for columna in columnas_permiso:

            if df[columna].isna().any():

                st.error(
                    f"❌ Hay registros sin {columna}"
                )

                return

        duplicados = df[
            ["id_rol", "id_modulo"]
        ].duplicated(keep=False)

        if not duplicados.empty:

            st.warning(
                "⚠️ Hay permisos duplicados por rol/módulo en el archivo"
            )

            st.dataframe(
                df[duplicados],
                use_container_width=True
            )

            return

    db_nombre = DB_POR_TABLA[tabla]

    db_path = get_db_path(db_nombre)

    st.markdown("---")

    st.write("📂 Base destino:")

    st.code(str(db_path))

    st.write("📋 Tabla destino:")

    st.code(tabla)

    confirmar = st.checkbox(
        "Confirmo que deseo agregar esta información",
        key="confirmar_carga_inicial"
    )

    if not confirmar:

        st.info(
            "Marca la confirmación para habilitar la carga."
        )

        return

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
