
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from sigem_db import get_db_path

def obtener_cancelaciones_pendientes():

    conn = sqlite3.connect(
        get_db_path("logistica")
    )

    query = '''
        SELECT
            folio_cancelacion,
            folio_embarque,
            folio_entrada_almacen,
            codigo_transporte,
            cliente,
            destino,
            motivo_cancelacion,
            fecha_cancelacion,
            estatus_inventarios
        FROM cancelaciones_embarque
        WHERE estatus_inventarios IS NULL
           OR estatus_inventarios = ''
           OR estatus_inventarios = 'Pendiente'
        ORDER BY fecha_cancelacion DESC
    '''

    df = pd.read_sql_query(
        query,
        conn
    )

    conn.close()

    return df


def obtener_detalle_embarque(
    folio_embarque
):

    conn = sqlite3.connect(
        get_db_path("logistica")
    )

    query = '''
        SELECT
            codigo_material,
            descripcion,
            cantidad_embarcar,
            bodega,
            ubicacion
        FROM detalle_embarque
        WHERE folio_embarque = ?
    '''

    df = pd.read_sql_query(
        query,
        conn,
        params=[folio_embarque]
    )

    conn.close()

    return df


def generar_folio_movimiento():

    fecha = datetime.now().strftime(
        "%Y%m%d%H%M%S"
    )

    return f"ENT-CANC-EMB-{fecha}"


def confirmacion_cancelacion_embarque_app():

    st.title(
        "✅ Confirmación cancelación embarque"
    )

    st.caption(
        "Entrada inventario por cancelación de embarque."
    )

    st.divider()

    df_cancelaciones = (
        obtener_cancelaciones_pendientes()
    )

    if df_cancelaciones.empty:

        st.info(
            "No existen cancelaciones pendientes."
        )

        return

    st.subheader(
        "📋 Folios pendientes"
    )

    df_cancelaciones["seleccionar"] = False

    df_editor = st.data_editor(

        df_cancelaciones,

        hide_index=True,

        use_container_width=True,

        height=400
    )

    df_sel = df_editor[
        df_editor["seleccionar"] == True
    ]

    if len(df_sel) != 1:

        st.warning(
            "Selecciona un folio."
        )

        return

    row_cancelacion = df_sel.iloc[0]

    st.divider()

    st.subheader(
        "📦 Materiales"
    )

    df_detalle = obtener_detalle_embarque(
        row_cancelacion["folio_embarque"]
    )

    st.dataframe(
        df_detalle,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    confirmar = st.button(
        "✅ Confirmar entrada inventario",
        use_container_width=True
    )

    if confirmar:

        st.success(
            "✅ Movimiento generado correctamente."
        )

        st.download_button(
            label="📥 Descargar Excel",
            data=df_detalle.to_csv(
                index=False
            ),
            file_name="entrada_cancelacion_embarque.csv",
            mime="text/csv"
        )

        st.info(
            "🖨️ Documento listo para impresión."
        )
#
