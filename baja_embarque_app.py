
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from io import BytesIO

from sigem_db import get_db_path


# =====================================================
# UTILIDADES
# =====================================================

def get_conn_logistica():

    conn = sqlite3.connect(
        get_db_path("logistica")
    )

    conn.row_factory = sqlite3.Row

    return conn


def obtener_columnas_tabla(conn, tabla):

    df_cols = pd.read_sql_query(
        f"PRAGMA table_info({tabla})",
        conn
    )

    return df_cols["name"].tolist()


def crear_tablas_baja_embarque():

    conn = get_conn_logistica()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS motivos_baja_embarque (
            id_motivo INTEGER PRIMARY KEY AUTOINCREMENT,
            motivo TEXT UNIQUE,
            activo INTEGER DEFAULT 1
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS solicitudes_baja_embarque (
            id_solicitud INTEGER PRIMARY KEY AUTOINCREMENT,
            folio_solicitud TEXT UNIQUE,
            folio_embarque TEXT,
            fecha_solicitud TEXT,
            usuario_solicitud TEXT,
            motivo TEXT,
            observaciones TEXT,
            estatus_solicitud TEXT,
            folio_notificacion_inventarios TEXT,
            fecha_creacion TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS notificaciones_inventario (
            id_notificacion INTEGER PRIMARY KEY AUTOINCREMENT,
            folio_notificacion TEXT UNIQUE,
            origen TEXT,
            tipo_documento TEXT,
            folio_origen TEXT,
            fecha_notificacion TEXT,
            usuario_solicita TEXT,
            estatus TEXT,
            observaciones TEXT
        )
        """
    )

    motivos_base = [
        "Error en captura del embarque",
        "Cliente cancela pedido",
        "Material no requerido",
        "Duplicidad de embarque",
        "Cambio de ruta o destino",
        "Reproceso operativo",
        "Otro"
    ]

    for motivo in motivos_base:

        cursor.execute(
            """
            INSERT OR IGNORE INTO motivos_baja_embarque (
                motivo,
                activo
            )
            VALUES (?, 1)
            """,
            (motivo,)
        )

    conn.commit()
    conn.close()


def generar_folio_solicitud_baja():

    fecha = datetime.now().strftime("%Y%m%d%H%M%S")

    return f"SOL-BE-{fecha}"


def generar_folio_notificacion_inventarios():

    fecha = datetime.now().strftime("%Y%m%d%H%M%S")

    return f"NINV-BE-{fecha}"


def obtener_motivos_baja():

    conn = get_conn_logistica()

    df = pd.read_sql_query(
        """
        SELECT motivo
        FROM motivos_baja_embarque
        WHERE activo = 1
        ORDER BY motivo
        """,
        conn
    )

    conn.close()

    return df["motivo"].tolist()


def obtener_embarques_disponibles_baja():

    conn = get_conn_logistica()

    columnas = obtener_columnas_tabla(
        conn,
        "embarques"
    )

    columnas_select = []

    columnas_deseadas = [
        "folio_embarque",
        "folio_hoja_carga",
        "pedido",
        "cliente",
        "destino",
        "codigo_transporte",
        "transportista",
        "vehiculo",
        "placas",
        "operador",
        "estatus",
        "fecha",
        "fecha_creacion"
    ]

    for col in columnas_deseadas:

        if col in columnas:

            columnas_select.append(col)

    if not columnas_select:

        conn.close()
        return pd.DataFrame()

    sql = f"""
        SELECT
            {', '.join(columnas_select)}
        FROM embarques
        WHERE 1 = 1
    """

    if "estatus" in columnas:

        sql += """
            AND IFNULL(estatus, '') NOT IN (
                'Cancelado',
                'Solicitud Cancelación',
                'Pendiente Inventarios'
            )
        """

    if "codigo_transporte" in columnas:

        sql += """
            AND (
                codigo_transporte IS NULL
                OR TRIM(codigo_transporte) = ''
            )
        """

    sql += """
        ORDER BY folio_embarque DESC
    """

    df = pd.read_sql_query(
        sql,
        conn
    )

    conn.close()

    return df


def obtener_embarques_bloqueados_transporte():

    conn = get_conn_logistica()

    columnas = obtener_columnas_tabla(
        conn,
        "embarques"
    )

    if "codigo_transporte" not in columnas:

        conn.close()
        return pd.DataFrame()

    columnas_mostrar = [
        col
        for col in [
            "folio_embarque",
            "cliente",
            "destino",
            "codigo_transporte",
            "transportista",
            "vehiculo",
            "placas",
            "estatus"
        ]
        if col in columnas
    ]

    df = pd.read_sql_query(
        f"""
        SELECT
            {', '.join(columnas_mostrar)}
        FROM embarques
        WHERE codigo_transporte IS NOT NULL
          AND TRIM(codigo_transporte) <> ''
          AND IFNULL(estatus, '') NOT IN ('Cancelado')
        ORDER BY folio_embarque DESC
        """,
        conn
    )

    conn.close()

    return df


def obtener_detalle_embarque(folio_embarque):

    conn = get_conn_logistica()

    try:

        df = pd.read_sql_query(
            """
            SELECT *
            FROM detalle_embarque
            WHERE folio_embarque = ?
            """,
            conn,
            params=(folio_embarque,)
        )

    except Exception:

        df = pd.DataFrame()

    conn.close()

    return df


def existe_solicitud_activa(folio_embarque):

    conn = get_conn_logistica()

    row = conn.execute(
        """
        SELECT folio_solicitud
        FROM solicitudes_baja_embarque
        WHERE folio_embarque = ?
          AND estatus_solicitud IN (
              'Pendiente Inventarios',
              'Solicitud Cancelación'
          )
        ORDER BY id_solicitud DESC
        LIMIT 1
        """,
        (folio_embarque,)
    ).fetchone()

    conn.close()

    return row


def actualizar_estatus_embarque(conn, folio_embarque, estatus):

    columnas = obtener_columnas_tabla(
        conn,
        "embarques"
    )

    campos = []
    valores = []

    if "estatus" in columnas:

        campos.append("estatus = ?")
        valores.append(estatus)

    if "fecha_estatus" in columnas:

        campos.append("fecha_estatus = ?")
        valores.append(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

    if "usuario_estatus" in columnas:

        campos.append("usuario_estatus = ?")
        valores.append(
            st.session_state.get("usuario", "SIN_USUARIO")
        )

    if not campos:

        return

    valores.append(folio_embarque)

    sql = f"""
        UPDATE embarques
        SET {', '.join(campos)}
        WHERE folio_embarque = ?
    """

    conn.execute(
        sql,
        valores
    )


def generar_excel_baja(
    embarque,
    detalle_df,
    folio_solicitud,
    folio_notificacion,
    motivo,
    observaciones
):

    salida = BytesIO()

    resumen = pd.DataFrame(
        [
            {
                "folio_solicitud": folio_solicitud,
                "folio_notificacion_inventarios": folio_notificacion,
                "folio_embarque": embarque.get("folio_embarque", ""),
                "folio_hoja_carga": embarque.get("folio_hoja_carga", ""),
                "pedido": embarque.get("pedido", ""),
                "cliente": embarque.get("cliente", ""),
                "destino": embarque.get("destino", ""),
                "motivo": motivo,
                "observaciones": observaciones,
                "estatus_solicitud": "Pendiente Inventarios",
                "usuario_solicitud": st.session_state.get(
                    "usuario",
                    "SIN_USUARIO"
                ),
                "fecha_solicitud": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            }
        ]
    )

    with pd.ExcelWriter(
        salida,
        engine="openpyxl"
    ) as writer:

        resumen.to_excel(
            writer,
            sheet_name="Solicitud baja",
            index=False
        )

        if detalle_df is not None and not detalle_df.empty:

            detalle_df.to_excel(
                writer,
                sheet_name="Detalle embarque",
                index=False
            )

    salida.seek(0)

    return salida.getvalue()


def registrar_solicitud_baja(
    embarque,
    motivo,
    observaciones
):

    conn = get_conn_logistica()

    folio_embarque = embarque.get(
        "folio_embarque",
        ""
    )

    folio_solicitud = generar_folio_solicitud_baja()
    folio_notificacion = generar_folio_notificacion_inventarios()

    fecha_actual = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    usuario = st.session_state.get(
        "usuario",
        "SIN_USUARIO"
    )

    try:

        conn.execute(
            """
            INSERT INTO solicitudes_baja_embarque (
                folio_solicitud,
                folio_embarque,
                fecha_solicitud,
                usuario_solicitud,
                motivo,
                observaciones,
                estatus_solicitud,
                folio_notificacion_inventarios,
                fecha_creacion
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                folio_solicitud,
                folio_embarque,
                fecha_actual,
                usuario,
                motivo,
                observaciones,
                "Pendiente Inventarios",
                folio_notificacion,
                fecha_actual
            )
        )

        conn.execute(
            """
            INSERT INTO notificaciones_inventario (
                folio_notificacion,
                origen,
                tipo_documento,
                folio_origen,
                fecha_notificacion,
                usuario_solicita,
                estatus,
                observaciones
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                folio_notificacion,
                "Logistica",
                "Solicitud baja embarque",
                folio_embarque,
                fecha_actual,
                usuario,
                "Pendiente Inventarios",
                observaciones
            )
        )

        actualizar_estatus_embarque(
            conn,
            folio_embarque,
            "Pendiente Inventarios"
        )

        conn.commit()

    except Exception as e:

        conn.rollback()
        conn.close()
        raise e

    conn.close()

    detalle_df = obtener_detalle_embarque(
        folio_embarque
    )

    excel = generar_excel_baja(
        embarque,
        detalle_df,
        folio_solicitud,
        folio_notificacion,
        motivo,
        observaciones
    )

    return {
        "folio_solicitud": folio_solicitud,
        "folio_notificacion": folio_notificacion,
        "excel": excel
    }


# =====================================================
# APP BAJA EMBARQUE
# =====================================================

def baja_embarque_app():

    crear_tablas_baja_embarque()

    st.subheader("❌ Solicitud de baja de embarque")

    st.info(
        """
        Logística solo genera la solicitud de baja.
        Inventarios debe validar el material y cerrar la cancelación.
        """
    )

    st.divider()

    try:

        df_embarques = obtener_embarques_disponibles_baja()
        motivos = obtener_motivos_baja()

    except Exception as e:

        st.error(
            "❌ Error cargando embarques disponibles para baja."
        )

        st.exception(e)

        return

    if df_embarques.empty:

        st.warning(
            "No existen embarques disponibles para solicitud de baja directa."
        )

        st.caption(
            "Los embarques asignados a transporte primero deben liberarse desde el proceso de transporte."
        )

        bloqueados = obtener_embarques_bloqueados_transporte()

        if not bloqueados.empty:

            st.markdown(
                "### 🚛 Embarques bloqueados por transporte"
            )

            st.dataframe(
                bloqueados,
                use_container_width=True,
                hide_index=True
            )

        return

    df_embarques = df_embarques.copy()
    df_embarques["seleccionar"] = False

    columnas = [
        "seleccionar"
    ] + [
        c for c in df_embarques.columns
        if c != "seleccionar"
    ]

    st.markdown("### 📦 Selecciona embarque")

    df_editor = st.data_editor(
        df_embarques[columnas],
        hide_index=True,
        use_container_width=True,
        height=360,
        column_config={
            "seleccionar": st.column_config.CheckboxColumn(
                "Sel.",
                default=False
            )
        },
        disabled=[
            c for c in columnas
            if c != "seleccionar"
        ],
        key="editor_baja_embarque"
    )

    seleccionados = df_editor[
        df_editor["seleccionar"] == True
    ]

    if len(seleccionados) == 0:

        st.info(
            "Selecciona un embarque para generar solicitud de baja."
        )

        return

    if len(seleccionados) > 1:

        st.warning(
            "Selecciona solo un embarque por solicitud."
        )

        return

    folio_embarque = seleccionados.iloc[0][
        "folio_embarque"
    ]

    solicitud_existente = existe_solicitud_activa(
        folio_embarque
    )

    if solicitud_existente:

        st.warning(
            f"El embarque ya tiene una solicitud activa: {solicitud_existente['folio_solicitud']}"
        )

        return

    embarque = seleccionados.iloc[0].to_dict()

    st.divider()

    st.markdown("### 🧾 Datos de solicitud")

    col1, col2 = st.columns(2)

    with col1:

        motivo = st.selectbox(
            "Motivo de baja *",
            motivos
        )

    with col2:

        confirmar = st.checkbox(
            "Confirmo que el embarque no está asignado a transporte"
        )

    observaciones = st.text_area(
        "Observaciones",
        placeholder="Describe el motivo operativo de la solicitud..."
    )

    detalle_df = obtener_detalle_embarque(
        folio_embarque
    )

    with st.expander(
        "📋 Detalle del embarque",
        expanded=False
    ):

        if detalle_df.empty:

            st.info(
                "No se encontró detalle del embarque."
            )

        else:

            st.dataframe(
                detalle_df,
                use_container_width=True,
                hide_index=True
            )

    st.divider()

    if st.button(
        "📨 Generar solicitud a Inventarios",
        use_container_width=True,
        disabled=not confirmar
    ):

        if not motivo:

            st.warning(
                "Selecciona un motivo de baja."
            )

            return

        try:

            resultado = registrar_solicitud_baja(
                embarque,
                motivo,
                observaciones
            )

            st.success(
                "✅ Solicitud de baja generada correctamente."
            )

            st.write(
                "Folio solicitud:",
                resultado["folio_solicitud"]
            )

            st.write(
                "Folio notificación inventarios:",
                resultado["folio_notificacion"]
            )

            st.download_button(
                label="📥 Descargar Excel solicitud baja",
                data=resultado["excel"],
                file_name=f"{resultado['folio_solicitud']}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:

            st.error(
                "❌ Error generando solicitud de baja."
            )

            st.exception(e)


if __name__ == "__main__":

    baja_embarque_app()
