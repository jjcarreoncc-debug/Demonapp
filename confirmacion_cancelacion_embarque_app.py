
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

    conn.commit()

    conn.close()


# =====================================================
# OBTENER SOLICITUDES
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
# DETALLE EMBARQUE
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
                "folio_embarque": solicitud.get("folio_embarque", ""),
                "cliente": solicitud.get("cliente", ""),
                "destino": solicitud.get("destino", ""),
                "usuario": st.session_state.get(
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
                "folio_documento": folio_documento,
                "folio_origen": solicitud.get("folio_embarque", ""),
                "codigo_material": row.get("codigo_material", ""),
                "descripcion": row.get("descripcion", ""),
                "cantidad": row.get("cantidad_embarcar", 0),
                "bodega": row.get("bodega", ""),
                "ubicacion": row.get("ubicacion", ""),
                "usuario": usuario,
                "fecha": fecha_actual
            }

            insertar_dinamico(
                conn_inv,
                "movimientos_inventario",
                datos_mov
            )

        conn_log.execute(
            """
            UPDATE embarques
            SET estatus = 'Cancelado'
            WHERE folio_embarque = ?
            """,
            (
                solicitud.get("folio_embarque", ""),
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

    st.divider()

    df_solicitudes = obtener_solicitudes_pendientes()

    if df_solicitudes.empty:

        st.info(
            "No existen cancelaciones pendientes."
        )

        return

    folio_sel = st.selectbox(
        "Selecciona solicitud",
        df_solicitudes["folio_solicitud"].tolist()
    )

    solicitud = df_solicitudes[
        df_solicitudes["folio_solicitud"] == folio_sel
    ].iloc[0].to_dict()

    st.dataframe(
        pd.DataFrame([solicitud]),
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    detalle_df = obtener_detalle_embarque(
        solicitud.get("folio_embarque", "")
    )

    st.markdown("### 📦 Materiales")

    st.dataframe(
        detalle_df,
        use_container_width=True,
        hide_index=True
    )

    confirmar = st.button(
        "✅ Confirmar entrada inventario",
        use_container_width=True
    )

    if confirmar:

        try:

            resultado = confirmar_entrada_cancelacion(
                solicitud,
                detalle_df
            )

            st.success(
                f"Documento generado: {resultado['folio_documento']}"
            )

            st.download_button(
                label="📥 Descargar Excel",
                data=resultado["excel"],
                file_name=f"{resultado['folio_documento']}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            st.markdown("### 🖨️ Documento para impresión")

            documento = f"""
==================================================
DOCUMENTO DE ENTRADA
==================================================

FOLIO:
{resultado['folio_documento']}

TIPO:
ENTRADA POR CANCELACION DE EMBARQUE

FOLIO EMBARQUE:
{solicitud.get('folio_embarque', '')}

CLIENTE:
{solicitud.get('cliente', '')}

DESTINO:
{solicitud.get('destino', '')}

USUARIO:
{st.session_state.get('usuario', '')}

FECHA:
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

==================================================
DETALLE
==================================================
"""

            for _, row in detalle_df.iterrows():

                documento += f"""

MATERIAL: {row.get('codigo_material', '')}
DESCRIPCION: {row.get('descripcion', '')}
CANTIDAD: {row.get('cantidad_embarcar', 0)}
BODEGA: {row.get('bodega', '')}
UBICACION: {row.get('ubicacion', '')}

--------------------------------------------------
"""

            documento += """

==================================================
ESTATUS FINAL
==================================================

HOJA DE CARGA CANCELADA
ENTRADA INVENTARIO CONFIRMADA

==================================================
"""

            st.download_button(
                label="📄 Descargar documento entrada",
                data=documento,
                file_name=f"{resultado['folio_documento']}.txt",
                mime="text/plain"
            )

        except Exception as e:

            st.error(
                "❌ Error confirmando entrada."
            )

            st.exception(e)


if __name__ == "__main__":

    confirmacion_cancelacion_embarque_app()
