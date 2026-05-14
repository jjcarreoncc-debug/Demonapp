import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from io import BytesIO

from sigem_db import get_db_path


# =====================================================
# UTILIDADES
# =====================================================

def obtener_columnas_tabla(conn, tabla):

    df_cols = pd.read_sql_query(
        f"PRAGMA table_info({tabla})",
        conn
    )

    return df_cols["name"].tolist()


def insertar_dinamico(conn, tabla, datos):

    columnas_tabla = obtener_columnas_tabla(conn, tabla)

    datos_filtrados = {
        k: v
        for k, v in datos.items()
        if k in columnas_tabla
    }

    if not datos_filtrados:
        return

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

    valores = [datos_filtrados[col] for col in columnas]

    conn.execute(sql, valores)


# =====================================================
# CONSULTAS
# =====================================================

def obtener_embarques_pendientes():

    conn = sqlite3.connect(get_db_path("logistica"))

    query = """
        SELECT
            e.folio_embarque,
            e.folio_hoja_carga,
            e.pedido,
            e.fecha,
            e.cliente,
            e.destino,
            e.transportista,
            e.vehiculo,
            e.placas,
            e.operador,
            e.ruta,
            e.estatus,
            COUNT(d.codigo_material) AS materiales,
            ROUND(COALESCE(SUM(d.peso), 0), 2) AS peso_total,
            ROUND(COALESCE(SUM(d.volumen), 0), 2) AS volumen_total
        FROM embarques e
        LEFT JOIN detalle_embarque d
            ON e.folio_embarque = d.folio_embarque
        WHERE e.estatus IN (
            'Pendiente carga',
            'En almacén',
            'Pendiente'
        )
        GROUP BY
            e.folio_embarque,
            e.folio_hoja_carga,
            e.pedido,
            e.fecha,
            e.cliente,
            e.destino,
            e.transportista,
            e.vehiculo,
            e.placas,
            e.operador,
            e.ruta,
            e.estatus
        ORDER BY e.fecha DESC
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


def obtener_detalle_embarque(folio_embarque):

    conn = sqlite3.connect(get_db_path("logistica"))

    query = """
        SELECT
            folio_embarque,
            folio_hoja_carga,
            folio_ruta,
            pedido,
            codigo_material,
            descripcion,
            cantidad_pedida,
            cantidad_embarcar,
            peso,
            volumen,
            bodega,
            ubicacion
        FROM detalle_embarque
        WHERE folio_embarque = ?
        ORDER BY codigo_material
    """

    df = pd.read_sql_query(
        query,
        conn,
        params=[folio_embarque]
    )

    conn.close()

    return df


def generar_excel_hoja_embarque(embarque, detalle):

    output = BytesIO()

    df_resumen = pd.DataFrame([embarque])

    with pd.ExcelWriter(output, engine="openpyxl") as writer:

        df_resumen.to_excel(
            writer,
            sheet_name="Resumen embarque",
            index=False
        )

        detalle.to_excel(
            writer,
            sheet_name="Detalle carga",
            index=False
        )

    output.seek(0)

    return output


# =====================================================
# CONFIRMAR CARGA / SALIDA INVENTARIO
# =====================================================

def confirmar_carga_embarque(embarque, detalle):

    conn_inv = sqlite3.connect(get_db_path("inventarios"))
    conn_log = sqlite3.connect(get_db_path("logistica"))

    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    folio_embarque = embarque["folio_embarque"]

    try:

        for _, row in detalle.iterrows():

            cantidad = row.get("cantidad_embarcar", 0)

            datos_movimiento = {
                "fecha": fecha_actual,
                "tipo_movimiento": "SALIDA",
                "codigo_material": row.get("codigo_material", ""),
                "descripcion": row.get("descripcion", ""),
                "cantidad": float(cantidad) * -1,
                "folio_movimiento": folio_embarque,
                "tipo_documento": "EMBARQUE",
                "numero_documento": folio_embarque,
                "referencia": "Venta por embarque",
                "comentarios": "Salida generada por confirmación de carga de embarque",
                "usuario": "admin"
            }

            insertar_dinamico(
                conn_inv,
                "movimientos_inventario",
                datos_movimiento
            )

        conn_log.execute("""
            UPDATE embarques
            SET
                estatus = 'Cargado',
                fecha_estatus = ?,
                usuario_estatus = ?,
                observaciones_estatus = ?
            WHERE folio_embarque = ?
        """, (
            fecha_actual,
            "admin",
            "Carga física confirmada por Inventarios",
            folio_embarque
        ))

        conn_log.execute("""
            UPDATE notificaciones_inventarios
            SET
                estatus = 'Atendida'
            WHERE folio_embarque = ?
        """, (
            folio_embarque,
        ))

        conn_inv.commit()
        conn_log.commit()

    except Exception as e:

        conn_inv.rollback()
        conn_log.rollback()
        conn_inv.close()
        conn_log.close()

        raise e

    conn_inv.close()
    conn_log.close()

    return {
        "ok": True,
        "mensaje": f"✅ Embarque cargado y salida registrada: {folio_embarque}"
    }


# =====================================================
# APP
# =====================================================

def embarques_inventario_app():

    st.title("📦 Embarques - Carga física")

    st.caption(
        "Inventarios / Salidas / Embarques"
    )

    st.divider()

    try:

        df_embarques = obtener_embarques_pendientes()

    except Exception as e:

        st.error("❌ Error consultando embarques pendientes.")
        st.exception(e)
        return

    if df_embarques.empty:

        st.warning("No existen embarques pendientes de carga.")
        return

    df_embarques["seleccionar"] = False

    tab_pendientes, tab_detalle, tab_confirmar = st.tabs(
        [
            "📦 Embarques pendientes",
            "📋 Detalle embarque",
            "✅ Confirmar carga"
        ]
    )

    with tab_pendientes:

        st.subheader("📦 Embarques pendientes de carga")

        columnas = [
            "seleccionar",
            "folio_embarque",
            "folio_hoja_carga",
            "cliente",
            "destino",
            "vehiculo",
            "placas",
            "operador",
            "materiales",
            "peso_total",
            "volumen_total",
            "estatus"
        ]

        df_editor = st.data_editor(
            df_embarques[columnas],
            hide_index=True,
            use_container_width=True,
            height=420,
            column_config={
                "seleccionar": st.column_config.CheckboxColumn(
                    "Sel.",
                    default=False
                ),
                "folio_embarque": "Embarque",
                "folio_hoja_carga": "Hoja carga",
                "cliente": "Cliente",
                "destino": "Destino",
                "vehiculo": "Vehículo",
                "placas": "Placas",
                "operador": "Operador",
                "materiales": "Mat.",
                "peso_total": "Peso",
                "volumen_total": "Vol.",
                "estatus": "Estatus"
            },
            disabled=[
                "folio_embarque",
                "folio_hoja_carga",
                "cliente",
                "destino",
                "vehiculo",
                "placas",
                "operador",
                "materiales",
                "peso_total",
                "volumen_total",
                "estatus"
            ],
            key="editor_embarques_inventario"
        )

        df_sel = df_editor[
            df_editor["seleccionar"] == True
        ]

        if df_sel.empty:

            st.info("Selecciona un embarque para revisar o confirmar.")

        elif len(df_sel) > 1:

            st.error("Selecciona solo un embarque.")

        else:

            st.success(
                f"Embarque seleccionado: {df_sel.iloc[0]['folio_embarque']}"
            )

    with tab_detalle:

        st.subheader("📋 Detalle del embarque")

        if "df_sel" not in locals() or df_sel.empty:

            st.info("Primero selecciona un embarque en la pestaña Embarques pendientes.")

        elif len(df_sel) > 1:

            st.warning("Selecciona solo un embarque.")

        else:

            embarque = df_sel.iloc[0].to_dict()

            detalle = obtener_detalle_embarque(
                embarque["folio_embarque"]
            )

            c1, c2, c3, c4 = st.columns(4)

            c1.metric("📦 Embarque", embarque["folio_embarque"])
            c2.metric("📋 Materiales", len(detalle))
            c3.metric("⚖️ Peso", embarque["peso_total"])
            c4.metric("📐 Volumen", embarque["volumen_total"])

            st.markdown("---")

            st.write(f"**Cliente:** {embarque['cliente']}")
            st.write(f"**Destino:** {embarque['destino']}")
            st.write(f"**Vehículo:** {embarque['vehiculo']}")
            st.write(f"**Placas:** {embarque['placas']}")
            st.write(f"**Operador:** {embarque['operador']}")

            st.markdown("---")

            st.dataframe(
                detalle,
                use_container_width=True,
                hide_index=True
            )

            excel = generar_excel_hoja_embarque(
                embarque,
                detalle
            )

            st.download_button(
                label="📥 Descargar hoja de embarque almacén",
                data=excel,
                file_name=f"hoja_embarque_{embarque['folio_embarque']}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    with tab_confirmar:

        st.subheader("✅ Confirmar carga física de embarque")

        if "df_sel" not in locals() or df_sel.empty:

            st.info("Primero selecciona un embarque.")

        elif len(df_sel) > 1:

            st.warning("Selecciona solo un embarque.")

        else:

            embarque = df_sel.iloc[0].to_dict()

            detalle = obtener_detalle_embarque(
                embarque["folio_embarque"]
            )

            st.warning(
                "Al confirmar, Inventarios registrará la salida por embarque."
            )

            c1, c2, c3 = st.columns(3)

            c1.metric("📦 Embarque", embarque["folio_embarque"])
            c2.metric("⚖️ Peso", embarque["peso_total"])
            c3.metric("📐 Volumen", embarque["volumen_total"])

            st.markdown("---")

            st.write(f"**Cliente:** {embarque['cliente']}")
            st.write(f"**Destino:** {embarque['destino']}")
            st.write(f"**Transporte:** {embarque['vehiculo']} / {embarque['placas']}")
            st.write(f"**Operador:** {embarque['operador']}")

            confirmar = st.checkbox(
                "Confirmo que el embarque fue cargado físicamente",
                key="confirmar_carga_fisica_embarque"
            )

            if not confirmar:

                st.info("Marca la confirmación para habilitar el proceso.")
                return

            if st.button(
                "✅ Confirmar carga de embarque",
                use_container_width=True
            ):

                try:

                    resultado = confirmar_carga_embarque(
                        embarque,
                        detalle
                    )

                    st.success(resultado["mensaje"])

                except Exception as e:

                    st.error("❌ Error confirmando carga de embarque.")
                    st.exception(e)


if __name__ == "__main__":

    embarques_inventario_app()
