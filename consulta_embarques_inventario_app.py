import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from io import BytesIO

from sigem_db import get_db_path


# =====================================================
# CONSULTA EMBARQUES CARGADOS
# =====================================================

def obtener_embarques_cargados():

    conn = sqlite3.connect(
        get_db_path("logistica")
    )

    inventarios_db = get_db_path("inventarios")

    conn.execute(
        f"ATTACH DATABASE '{inventarios_db}' AS inv"
    )

    query = """
        SELECT
            e.folio_embarque,
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

            ROUND(
                COALESCE(SUM(d.cantidad_embarcar), 0),
                2
            ) AS cantidad_total,

            ROUND(
                COALESCE(SUM(d.peso), 0),
                2
            ) AS peso_total,

            ROUND(
                COALESCE(SUM(d.volumen), 0),
                2
            ) AS volumen_total,

            COUNT(
                DISTINCT inv.numero_documento
            ) AS movimientos_inventario

        FROM embarques e

        LEFT JOIN detalle_embarque d
            ON e.folio_embarque = d.folio_embarque

        LEFT JOIN inv.movimientos_inventario inv
            ON inv.numero_documento = e.folio_embarque
            AND inv.tipo_documento = 'EMBARQUE'

        WHERE e.estatus = 'Cargado'

        GROUP BY
            e.folio_embarque,
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

    conn = sqlite3.connect(
        get_db_path("logistica")
    )

    query = """
        SELECT
            folio_embarque,
            codigo_material,
            descripcion,
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


# =====================================================
# EXPORTAR EXCEL
# =====================================================

def generar_excel_embarque(
    embarque,
    detalle
):

    output = BytesIO()

    df_resumen = pd.DataFrame([embarque])

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

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


# =====================================================
# APP
# =====================================================

def consulta_embarques_inventario_app():

    st.title(
        "📋 Consulta embarques cargados"
    )

    st.caption(
        "Inventarios / Salidas / Embarques / Consulta"
    )

    st.divider()

    try:

        df = obtener_embarques_cargados()

    except Exception as e:

        st.error(
            "❌ Error consultando embarques."
        )

        st.exception(e)

        return

    if df.empty:

        st.warning(
            "No existen embarques cargados."
        )

        return

    # =================================================
    # KPIs
    # =================================================

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "🚚 Embarques",
        len(df)
    )

    c2.metric(
        "📦 Materiales",
        int(df["materiales"].sum())
    )

    c3.metric(
        "⚖️ Peso",
        round(df["peso_total"].sum(), 2)
    )

    c4.metric(
        "📐 Volumen",
        round(df["volumen_total"].sum(), 2)
    )

    st.markdown("---")

    # =================================================
    # FILTROS
    # =================================================

    st.subheader("🔎 Filtros")

    f1, f2, f3, f4 = st.columns(4)

    filtro_cliente = f1.text_input(
        "Cliente"
    )

    filtro_embarque = f2.text_input(
        "Folio embarque"
    )

    filtro_operador = f3.text_input(
        "Operador"
    )

    filtro_placas = f4.text_input(
        "Placas"
    )

    if filtro_cliente:

        df = df[
            df["cliente"]
            .str.contains(
                filtro_cliente,
                case=False,
                na=False
            )
        ]

    if filtro_embarque:

        df = df[
            df["folio_embarque"]
            .astype(str)
            .str.contains(
                filtro_embarque,
                case=False,
                na=False
            )
        ]

    if filtro_operador:

        df = df[
            df["operador"]
            .astype(str)
            .str.contains(
                filtro_operador,
                case=False,
                na=False
            )
        ]

    if filtro_placas:

        df = df[
            df["placas"]
            .astype(str)
            .str.contains(
                filtro_placas,
                case=False,
                na=False
            )
        ]

    st.markdown("---")

    # =================================================
    # GRID
    # =================================================

    st.subheader(
        "📋 Embarques cargados"
    )

    df["seleccionar"] = False

    columnas = [
        "seleccionar",
        "folio_embarque",
        "fecha",
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
        df[columnas],
        hide_index=True,
        use_container_width=True,
        height=420,
        column_config={
            "seleccionar":
                st.column_config.CheckboxColumn(
                    "Sel.",
                    default=False
                )
        },
        disabled=[
            "folio_embarque",
            "fecha",
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
    )

    st.markdown("---")

    # =================================================
    # GRAFICAS
    # =================================================

    st.subheader(
        "📊 Dashboard embarques"
    )

    g1, g2 = st.columns(2)

    with g1:

        fig_clientes = px.bar(
            df,
            x="cliente",
            y="peso_total",
            title="Peso por cliente"
        )

        st.plotly_chart(
            fig_clientes,
            use_container_width=True
        )

    with g2:

        fig_operador = px.pie(
            df,
            names="operador",
            values="volumen_total",
            title="Volumen por operador"
        )

        st.plotly_chart(
            fig_operador,
            use_container_width=True
        )

    st.markdown("---")

    # =================================================
    # DETALLE
    # =================================================

    df_sel = df_editor[
        df_editor["seleccionar"] == True
    ]

    if df_sel.empty:

        st.info(
            "Selecciona un embarque."
        )

        return

    if len(df_sel) > 1:

        st.warning(
            "Selecciona solo un embarque."
        )

        return

    embarque = df_sel.iloc[0].to_dict()

    detalle = obtener_detalle_embarque(
        embarque["folio_embarque"]
    )

    st.subheader(
        f"📦 Detalle embarque: "
        f"{embarque['folio_embarque']}"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "📦 Materiales",
        len(detalle)
    )

    c2.metric(
        "⚖️ Peso",
        round(detalle["peso"].sum(), 2)
    )

    c3.metric(
        "📐 Volumen",
        round(detalle["volumen"].sum(), 2)
    )

    c4.metric(
        "🚚 Estatus",
        embarque["estatus"]
    )

    st.markdown("---")

    st.write(
        f"**Cliente:** {embarque['cliente']}"
    )

    st.write(
        f"**Destino:** {embarque['destino']}"
    )

    st.write(
        f"**Vehículo:** {embarque['vehiculo']}"
    )

    st.write(
        f"**Placas:** {embarque['placas']}"
    )

    st.write(
        f"**Operador:** {embarque['operador']}"
    )

    st.markdown("---")

    # =================================================
    # FLUJO OPERACIONAL
    # =================================================

    st.subheader(
        "🟢 Flujo operacional completado"
    )

    st.success(
        "🟢 Hoja de carga cerrada"
    )

    st.success(
        "🟢 Embarque confirmado por logística"
    )

    st.success(
        "🟢 Carga física confirmada por Inventarios"
    )

    st.success(
        "🟢 Salida inventario generada"
    )

    st.success(
        f"🟢 Documento inventario generado: "
        f"{embarque['folio_embarque']}"
    )

    st.success(
        "🟢 Proceso terminado"
    )

    st.markdown("---")

    st.subheader(
        "📦 Materiales embarcados"
    )

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
        file_name=(
            f"embarque_"
            f"{embarque['folio_embarque']}.xlsx"
        ),
        mime=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        )
    )


if __name__ == "__main__":

    consulta_embarques_inventario_app()
