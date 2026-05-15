
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from io import BytesIO
import base64

from sigem_db import get_db_path


# =====================================================
# CONEXIONES
# =====================================================

def get_conn_logistica():

    conn = sqlite3.connect(
        get_db_path("logistica")
    )

    conn.row_factory = sqlite3.Row

    return conn


def get_conn_inventarios():

    conn = sqlite3.connect(
        get_db_path("inventarios")
    )

    conn.row_factory = sqlite3.Row

    return conn


# =====================================================
# UTILIDADES DB
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


def insertar_dinamico(conn, tabla, datos):

    columnas_tabla = obtener_columnas_tabla(
        conn,
        tabla
    )

    datos_filtrados = {
        k: v
        for k, v in datos.items()
        if k in columnas_tabla
    }

    if not datos_filtrados:

        return False

    columnas = list(datos_filtrados.keys())

    placeholders = ",".join(["?"] * len(columnas))

    sql = f"""
        INSERT INTO {tabla} (
            {",".join(columnas)}
        )
        VALUES (
            {placeholders}
        )
    """

    valores = [
        datos_filtrados[col]
        for col in columnas
    ]

    conn.execute(
        sql,
        valores
    )

    return True


# =====================================================
# ASEGURAR TABLAS LOGISTICA
# =====================================================

def asegurar_tablas_logistica():

    conn = get_conn_logistica()

    cursor = conn.cursor()

    # =====================================================
    # SOLICITUDES BAJA EMBARQUE
    # =====================================================

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
            fecha_creacion TEXT,
            folio_movimiento_inventario TEXT,
            fecha_confirmacion_inventario TEXT,
            usuario_confirmacion_inventario TEXT

        )
        """
    )

    # =====================================================
    # NOTIFICACIONES INVENTARIO
    # =====================================================

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
            observaciones TEXT,
            fecha_confirmacion TEXT,
            usuario_confirmacion TEXT

        )
        """
    )

    # =====================================================
    # ALTER TABLE SOLICITUDES
    # =====================================================

    try:

        cursor.execute(
            """
            ALTER TABLE solicitudes_baja_embarque
            ADD COLUMN folio_movimiento_inventario TEXT
            """
        )

    except sqlite3.OperationalError:

        pass

    try:

        cursor.execute(
            """
            ALTER TABLE solicitudes_baja_embarque
            ADD COLUMN fecha_confirmacion_inventario TEXT
            """
        )

    except sqlite3.OperationalError:

        pass

    try:

        cursor.execute(
            """
            ALTER TABLE solicitudes_baja_embarque
            ADD COLUMN usuario_confirmacion_inventario TEXT
            """
        )

    except sqlite3.OperationalError:

        pass

    # =====================================================
    # ALTER TABLE NOTIFICACIONES
    # =====================================================

    try:

        cursor.execute(
            """
            ALTER TABLE notificaciones_inventario
            ADD COLUMN fecha_confirmacion TEXT
            """
        )

    except sqlite3.OperationalError:

        pass

    try:

        cursor.execute(
            """
            ALTER TABLE notificaciones_inventario
            ADD COLUMN usuario_confirmacion TEXT
            """
        )

    except sqlite3.OperationalError:

        pass

    conn.commit()

    conn.close()
# =====================================================
# OBTENER SOLICITUDES PENDIENTES
# =====================================================

def obtener_solicitudes_pendientes():

    asegurar_tablas_logistica()

    conn = get_conn_logistica()

    query = """
        SELECT

            s.folio_solicitud,
            s.folio_embarque,
            s.fecha_solicitud,
            s.usuario_solicitud,
            s.motivo,
            s.observaciones,
            s.estatus_solicitud,
            s.folio_notificacion_inventarios,

            e.folio_hoja_carga,
            e.pedido,
            e.cliente,
            e.destino,
            e.codigo_transporte,
            e.transportista,
            e.vehiculo,
            e.placas,
            e.operador,
            e.estatus AS estatus_embarque

        FROM solicitudes_baja_embarque s

        LEFT JOIN embarques e
            ON s.folio_embarque = e.folio_embarque

        WHERE IFNULL(s.estatus_solicitud, '') IN (
            'Pendiente Inventarios',
            'Solicitud Cancelación',
            'Pendiente'
        )

        ORDER BY s.id_solicitud DESC
    """

    df = pd.read_sql_query(
        query,
        conn
    )

    conn.close()

    return df


# =====================================================
# BUSCAR SOLICITUD POR FOLIO / CODIGO DE BARRAS
# =====================================================

def buscar_solicitud_por_folio(folio):

    asegurar_tablas_logistica()

    conn = get_conn_logistica()

    query = """
        SELECT

            s.folio_solicitud,
            s.folio_embarque,
            s.fecha_solicitud,
            s.usuario_solicitud,
            s.motivo,
            s.observaciones,
            s.estatus_solicitud,
            s.folio_notificacion_inventarios,

            e.folio_hoja_carga,
            e.pedido,
            e.cliente,
            e.destino,
            e.codigo_transporte,
            e.transportista,
            e.vehiculo,
            e.placas,
            e.operador,
            e.estatus AS estatus_embarque

        FROM solicitudes_baja_embarque s

        LEFT JOIN embarques e
            ON s.folio_embarque = e.folio_embarque

        WHERE s.folio_solicitud = ?
           OR s.folio_notificacion_inventarios = ?
           OR s.folio_embarque = ?

        ORDER BY s.id_solicitud DESC
        LIMIT 1
    """

    df = pd.read_sql_query(
        query,
        conn,
        params=(folio, folio, folio)
    )

    conn.close()

    return df


# =====================================================
# OBTENER DETALLE EMBARQUE
# =====================================================

def obtener_detalle_embarque(folio_embarque):

    conn = get_conn_logistica()

    try:

        df = pd.read_sql_query(
            """
            SELECT
                folio_embarque,
                folio_hoja_carga,
                pedido,
                codigo_material,
                descripcion,
                cantidad_embarcar,
                peso,
                volumen,
                bodega,
                ubicacion
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


# =====================================================
# GENERAR EXCEL
# =====================================================

def generar_excel_confirmacion(
    solicitud,
    detalle_df,
    folio_documento
):

    salida = BytesIO()

    resumen = pd.DataFrame(
        [
            {
                "folio_documento_entrada": folio_documento,
                "tipo_movimiento": "ENTRADA POR CANCELACION DE EMBARQUE",
                "folio_solicitud": solicitud.get("folio_solicitud", ""),
                "folio_notificacion_inventarios": solicitud.get(
                    "folio_notificacion_inventarios",
                    ""
                ),
                "folio_embarque": solicitud.get("folio_embarque", ""),
                "folio_hoja_carga": solicitud.get("folio_hoja_carga", ""),
                "pedido": solicitud.get("pedido", ""),
                "cliente": solicitud.get("cliente", ""),
                "destino": solicitud.get("destino", ""),
                "codigo_transporte": solicitud.get("codigo_transporte", ""),
                "motivo": solicitud.get("motivo", ""),
                "usuario_logistica": solicitud.get("usuario_solicitud", ""),
                "usuario_inventarios": st.session_state.get(
                    "usuario",
                    "SIN_USUARIO"
                ),
                "fecha_confirmacion": datetime.now().strftime(
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
            sheet_name="Documento entrada",
            index=False
        )

        if detalle_df is not None and not detalle_df.empty:

            detalle_df.to_excel(
                writer,
                sheet_name="Materiales",
                index=False
            )

    salida.seek(0)

    return salida.getvalue()


# =====================================================
# GENERAR BARCODE BASE64 OPCIONAL
# =====================================================

def generar_barcode_base64(folio_documento):

    try:

        import barcode
        from barcode.writer import ImageWriter

        buffer = BytesIO()

        code128 = barcode.get(
            "code128",
            folio_documento,
            writer=ImageWriter()
        )

        code128.write(
            buffer,
            options={
                "write_text": True,
                "module_height": 12,
                "font_size": 9,
                "quiet_zone": 2
            }
        )

        buffer.seek(0)

        return base64.b64encode(
            buffer.read()
        ).decode()

    except Exception:

        return None


# =====================================================
# DOCUMENTO IMPRIMIBLE
# =====================================================

# =====================================================
# CONFIRMAR ENTRADA
# =====================================================

def confirmar_entrada_cancelacion(
    solicitud,
    detalle_df
):

    folio_documento = solicitud.get(
        "folio_notificacion_inventarios",
        ""
    )

    if not folio_documento:

        folio_documento = solicitud.get(
            "folio_solicitud",
            ""
        )

    conn_inv = get_conn_inventarios()
    conn_log = get_conn_logistica()

    fecha_actual = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    usuario = st.session_state.get(
        "usuario",
        "SIN_USUARIO"
    )

    try:

        for _, row in detalle_df.iterrows():

            datos_mov = {
                "tipo_movimiento": "ENTRADA",
                "tipo": "ENTRADA",
                "motivo": "ENTRADA POR CANCELACION DE EMBARQUE",
                "concepto": "ENTRADA POR CANCELACION DE EMBARQUE",
                "folio_documento": folio_documento,
                "folio_origen": solicitud.get("folio_embarque", ""),
                "referencia": solicitud.get("folio_solicitud", ""),
                "codigo_material": row.get("codigo_material", ""),
                "descripcion": row.get("descripcion", ""),
                "cantidad": row.get("cantidad_embarcar", 0),
                "bodega": row.get("bodega", ""),
                "almacen": row.get("bodega", ""),
                "ubicacion": row.get("ubicacion", ""),
                "usuario": usuario,
                "fecha": fecha_actual,
                "fecha_movimiento": fecha_actual,
                "observaciones": "Entrada por cancelación de embarque"
            }

            insertado = insertar_dinamico(
                conn_inv,
                "movimientos_inventario",
                datos_mov
            )

            if not insertado:

                raise Exception(
                    "No se pudo insertar movimiento. Revisa columnas de movimientos_inventario."
                )

        conn_log.execute(
            """
            UPDATE solicitudes_baja_embarque
            SET
                estatus_solicitud = 'Confirmado Inventarios',
                folio_movimiento_inventario = ?,
                fecha_confirmacion_inventario = ?,
                usuario_confirmacion_inventario = ?
            WHERE folio_solicitud = ?
            """,
            (
                folio_documento,
                fecha_actual,
                usuario,
                solicitud.get("folio_solicitud", "")
            )
        )

        conn_log.execute(
            """
            UPDATE notificaciones_inventario
            SET
                estatus = 'Confirmado Inventarios',
                fecha_confirmacion = ?,
                usuario_confirmacion = ?
            WHERE folio_notificacion = ?
            """,
            (
                fecha_actual,
                usuario,
                solicitud.get("folio_notificacion_inventarios", "")
            )
        )

        conn_log.execute(
            """
            UPDATE embarques
            SET
                estatus = 'Cancelado',
                fecha_estatus = ?,
                usuario_estatus = ?
            WHERE folio_embarque = ?
            """,
            (
                fecha_actual,
                usuario,
                solicitud.get("folio_embarque", "")
            )
        )

        conn_inv.commit()
        conn_log.commit()

        conn_inv.close()
        conn_log.close()

        excel = generar_excel_confirmacion(
            solicitud,
            detalle_df,
            folio_documento
        )

        return {
            "folio_documento": folio_documento,
            "excel": excel
        }

    except Exception as e:

        conn_inv.rollback()
        conn_log.rollback()

        conn_inv.close()
        conn_log.close()

        raise e


# =====================================================
# APP
# =====================================================

def confirmacion_cancelacion_embarque_app():

    st.title(
        "✅ Confirmación cancelación embarque"
    )

    st.caption(
        "Inventarios confirma entrada por cancelación de embarque generada por Logística."
    )

    st.divider()

    tab_manual, tab_barcode = st.tabs(
        [
            "📋 Pendientes",
            "🔎 Código de barras"
        ]
    )

    solicitud = None

    with tab_manual:

        df_solicitudes = obtener_solicitudes_pendientes()

        if df_solicitudes.empty:

            st.info(
                "No existen cancelaciones pendientes."
            )

        else:

            df_solicitudes = df_solicitudes.copy()
            df_solicitudes["seleccionar"] = False

            columnas = [
                "seleccionar",
                "folio_solicitud",
                "folio_notificacion_inventarios",
                "folio_embarque",
                "folio_hoja_carga",
                "cliente",
                "destino",
                "codigo_transporte",
                "motivo",
                "fecha_solicitud",
                "estatus_solicitud"
            ]

            columnas = [
                c for c in columnas
                if c in df_solicitudes.columns
            ]

            df_editor = st.data_editor(
                df_solicitudes[columnas],
                hide_index=True,
                use_container_width=True,
                height=380,
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
                key="editor_confirmacion_cancelacion_embarque"
            )

            df_sel = df_editor[
                df_editor["seleccionar"] == True
            ]

            if len(df_sel) > 1:

                st.warning(
                    "Selecciona solo un folio."
                )

            elif len(df_sel) == 1:

                solicitud = df_sel.iloc[0].to_dict()

    with tab_barcode:

        folio_scan = st.text_input(
            "Escanea o captura folio",
            placeholder="Ejemplo: NINV-BE-20260515225201"
        )

        if folio_scan:

            df_scan = buscar_solicitud_por_folio(
                folio_scan.strip()
            )

            if df_scan.empty:

                st.warning(
                    "No se encontró el folio capturado."
                )

            else:

                solicitud = df_scan.iloc[0].to_dict()

                st.success(
                    "Folio encontrado."
                )

                st.dataframe(
                    df_scan,
                    use_container_width=True,
                    hide_index=True
                )

    if solicitud is None:

        return

    st.divider()

    st.markdown("### 📦 Detalle de materiales")

    detalle_df = obtener_detalle_embarque(
        solicitud.get("folio_embarque", "")
    )

    if detalle_df.empty:

        st.warning(
            "No se encontró detalle del embarque."
        )

        return

    st.dataframe(
        detalle_df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.markdown("### 🧾 Confirmación")

    confirmar_check = st.checkbox(
        "Confirmo que el material fue recibido en inventario"
    )

    confirmar = st.button(
        "✅ Confirmar entrada a inventario",
        use_container_width=True,
        disabled=not confirmar_check
    )

    if confirmar:

        try:

            resultado = confirmar_entrada_cancelacion(
                solicitud,
                detalle_df
            )

            st.success(
                f"✅ Entrada confirmada. Documento: {resultado['folio_documento']}"
            )

            st.download_button(
                label="📥 Descargar Excel documento entrada",
                data=resultado["excel"],
                file_name=f"{resultado['folio_documento']}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            st.markdown("### 🖨️ Documento para impresión")

            mostrar_documento_impresion(
                solicitud,
                detalle_df,
                resultado["folio_documento"]
            )

        except Exception as e:

            st.error(
                "❌ Error confirmando entrada por cancelación."
            )

            st.exception(e)


if __name__ == "__main__":

    confirmacion_cancelacion_embarque_app()
