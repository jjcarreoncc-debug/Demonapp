import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from io import BytesIO

from sigem_db import get_db_path


def obtener_embarques_cargados():

    conn = sqlite3.connect(get_db_path("logistica"))

    inventarios_db = get_db_path("inventarios")

    conn.execute(
        f"ATTACH DATABASE '{inventarios_db}' AS inv"
    )

    query = """
        WITH det AS (
            SELECT
                folio_embarque,
                COUNT(codigo_material) AS materiales,
                ROUND(COALESCE(SUM(cantidad_embarcar), 0), 2) AS cantidad_total,
                ROUND(COALESCE(SUM(peso), 0), 2) AS peso_total,
                ROUND(COALESCE(SUM(volumen), 0), 2) AS volumen_total
            FROM detalle_embarque
            GROUP BY folio_embarque
        ),

        mov AS (
            SELECT
                numero_documento,
                COUNT(*) AS movimientos_inventario,
                MIN(fecha) AS fecha_salida_inventario
            FROM inv.movimientos_inventario
            WHERE tipo_documento = 'EMBARQUE'
            GROUP BY numero_documento
        )

        SELECT
            e.folio_embarque,
            e.codigo_transporte,
            e.fecha,
            mov.fecha_salida_inventario,
            e.cliente,
            e.destino,
            e.transportista,
            e.vehiculo,
            e.placas,
            e.operador,
            e.ruta,
            e.estatus,
            COALESCE(det.materiales, 0) AS materiales,
            COALESCE(det.cantidad_total, 0) AS cantidad_total,
            COALESCE(det.peso_total, 0) AS peso_total,
            COALESCE(det.volumen_total, 0) AS volumen_total,
            COALESCE(mov.movimientos_inventario, 0) AS movimientos_inventario,
            e.folio_embarque AS documento_inventario

        FROM embarques e

        INNER JOIN mov
            ON mov.numero_documento = e.folio_embarque

        LEFT JOIN det
            ON det.folio_embarque = e.folio_embarque

        WHERE e.estatus = 'Cargado'

        ORDER BY
            e.codigo_transporte,
            mov.fecha_salida_inventario DESC
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


def obtener_detalle_embarque(folio_embarque):

    conn = sqlite3.connect(get_db_path("logistica"))

    inventarios_db = get_db_path("inventarios")

    conn.execute(
        f"ATTACH DATABASE '{inventarios_db}' AS inv"
    )

    query = """
        SELECT
            d.folio_embarque,
            d.codigo_material,
            d.descripcion,
            d.cantidad_embarcar,
            COALESCE(
                (
                    SELECT
                        SUM(ABS(m.cantidad))
                    FROM inv.movimientos_inventario m
                    WHERE m.numero_documento = d.folio_embarque
                      AND m.tipo_documento = 'EMBARQUE'
                      AND m.codigo_material = d.codigo_material
                ),
                0
            ) AS cantidad_descontada,
            d.peso,
            d.volumen,
            d.bodega,
            d.ubicacion

        FROM detalle_embarque d

        WHERE d.folio_embarque = ?

        ORDER BY d.codigo_material
    """

    df = pd.read_sql_query(
        query,
        conn,
        params=[folio_embarque]
    )

    conn.close()

    return df


def generar_excel_embarque(embarque, detalle):

    output = BytesIO()

    df_resumen = pd.DataFrame([embarque])

    with pd.ExcelWriter(output, engine="openpyxl") as writer:

        df_resumen.to_excel(
            writer,
            sheet_name="Resumen",
            index=False
        )

        detalle.to_excel(
            writer,
            sheet_name="Detalle",
            index=False
        )

    output.seek(0)

    return output


def mostrar_flujo_operacional(embarque):

    st.subheader("🟢 Flujo operacional completado")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.success("🟢 Hoja carga cerrada")
    col2.success("🟢 Logística confirmó")
    col3.success("🟢 Inventarios cargó")
    col4.success("🟢 Salida generada")
    col5.success("🟢 Terminado")

    st.info(
        f"Documento inventario generado: **{embarque['documento_inventario']}**"
    )


def consulta_embarques_inventario_app():

    st.title("📋 Consulta embarques cargados")

    st.caption(
        "Inventarios / Salidas / Embarques / Consulta"
    )

    st.divider()

    try:

        df = obtener_embarques_cargados()

    except Exception as e:

        st.error("❌ Error consultando embarques.")
        st.exception(e)
        return

    if df.empty:

        st.warning(
            "No existen embarques cargados con salida de inventario."
        )

        return

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("🚚 Transportes", df["codigo_transporte"].nunique())
    c2.metric("📦 Embarques", len(df))
    c3.metric("⚖️ Peso total", round(df["peso_total"].sum(), 2))
    c4.metric("📐 Volumen total", round(df["volumen_total"].sum(), 2))

    st.markdown("---")

    st.subheader("🔎 Filtros")

    f1, f2, f3, f4, f5 = st.columns(5)

    filtro_transporte = f1.text_input("Transporte")
    filtro_embarque = f2.text_input("Folio embarque")
    filtro_cliente = f3.text_input("Cliente")
    filtro_operador = f4.text_input("Operador")
    filtro_placas = f5.text_input("Placas")

    if filtro_transporte:
        df = df[
            df["codigo_transporte"]
            .astype(str)
            .str.contains(filtro_transporte, case=False, na=False)
        ]

    if filtro_embarque:
        df = df[
            df["folio_embarque"]
            .astype(str)
            .str.contains(filtro_embarque, case=False, na=False)
        ]

    if filtro_cliente:
        df = df[
            df["cliente"]
            .astype(str)
            .str.contains(filtro_cliente, case=False, na=False)
        ]

    if filtro_operador:
        df = df[
            df["operador"]
            .astype(str)
            .str.contains(filtro_operador, case=False, na=False)
        ]

    if filtro_placas:
        df = df[
            df["placas"]
            .astype(str)
            .str.contains(filtro_placas, case=False, na=False)
        ]

    st.markdown("---")

    st.subheader("📋 Embarques cargados por transporte")

    df["seleccionar"] = False

    columnas = [
        "seleccionar",
        "codigo_transporte",
        "folio_embarque",
        "documento_inventario",
        "fecha_salida_inventario",
        "cliente",
        "destino",
        "transportista",
        "vehiculo",
        "placas",
        "operador",
        "materiales",
        "peso_total",
        "volumen_total",
        "estatus"
    ]

    df_editor = st.data_editor(
        df[columnas],
        hide_index=True,
        use_container_width=True,
        height=420,
        column_config={
            "seleccionar": st.column_config.CheckboxColumn(
                "Sel.",
                default=False
            ),
            "codigo_transporte": "Transporte",
            "folio_embarque": "Embarque",
            "documento_inventario": "Doc. inventario",
            "fecha_salida_inventario": "Fecha salida inv.",
            "cliente": "Cliente",
            "destino": "Destino",
            "transportista": "Transportista",
            "vehiculo": "Vehículo",
            "placas": "Placas",
            "operador": "Operador",
            "materiales": "Mat.",
            "peso_total": "Peso",
            "volumen_total": "Vol.",
            "estatus": "Estatus"
        },
        disabled=[
            "codigo_transporte",
            "folio_embarque",
            "documento_inventario",
            "fecha_salida_inventario",
            "cliente",
            "destino",
            "transportista",
            "vehiculo",
            "placas",
            "operador",
            "materiales",
            "peso_total",
            "volumen_total",
            "estatus"
        ],
        key="consulta_embarques_cargados"
    )

    st.markdown("---")

    st.subheader("📊 Dashboard por transporte")

    g1, g2 = st.columns(2)

    with g1:

        df_peso = (
            df.groupby("codigo_transporte", as_index=False)["peso_total"]
            .sum()
        )

        fig_peso = px.bar(
            df_peso,
            x="codigo_transporte",
            y="peso_total",
            title="Peso cargado por transporte"
        )

        st.plotly_chart(
            fig_peso,
            use_container_width=True
        )

    with g2:

        df_volumen = (
            df.groupby("codigo_transporte", as_index=False)["volumen_total"]
            .sum()
        )

        fig_volumen = px.pie(
            df_volumen,
            names="codigo_transporte",
            values="volumen_total",
            title="Volumen por transporte"
        )

        st.plotly_chart(
            fig_volumen,
            use_container_width=True
        )

    st.markdown("---")

    df_sel = df_editor[
        df_editor["seleccionar"] == True
    ]

    if df_sel.empty:

        st.info("Selecciona un embarque para ver el detalle.")
        return

    if len(df_sel) > 1:

        st.warning("Selecciona solo un embarque.")
        return

    embarque = df_sel.iloc[0].to_dict()

    detalle = obtener_detalle_embarque(
        embarque["folio_embarque"]
    )

    st.subheader(
        f"🚚 Transporte {embarque['codigo_transporte']} / "
        f"Embarque {embarque['folio_embarque']}"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("📦 Materiales", len(detalle))
    c2.metric("⚖️ Peso", round(detalle["peso"].sum(), 2))
    c3.metric("📐 Volumen", round(detalle["volumen"].sum(), 2))
    c4.metric("🚚 Estatus", embarque["estatus"])

    st.markdown("---")

    st.write(f"**Transporte:** {embarque['codigo_transporte']}")
    st.write(f"**Transportista:** {embarque['transportista']}")
    st.write(f"**Vehículo:** {embarque['vehiculo']}")
    st.write(f"**Placas:** {embarque['placas']}")
    st.write(f"**Operador:** {embarque['operador']}")
    st.write(f"**Cliente:** {embarque['cliente']}")
    st.write(f"**Destino:** {embarque['destino']}")
    st.write(f"**Documento inventario:** {embarque['documento_inventario']}")
    st.write(f"**Fecha salida inventario:** {embarque['fecha_salida_inventario']}")

    st.markdown("---")

    mostrar_flujo_operacional(embarque)

    st.markdown("---")

    st.subheader("📦 Materiales embarcados y descontados")

    st.dataframe(
        detalle,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    excel = generar_excel_embarque(
        embarque,
        detalle
    )

    st.download_button(
        label="📥 Descargar embarque Excel",
        data=excel,
        file_name=f"embarque_{embarque['folio_embarque']}.xlsx",
        mime=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        )
    )


if __name__ == "__main__":

    consulta_embarques_inventario_app()
