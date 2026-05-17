import streamlit as st
import pandas as pd
import sqlite3
import altair as alt
from io import BytesIO
from datetime import datetime

from openpyxl import Workbook
from openpyxl.styles import (
    Font,
    PatternFill,
    Alignment,
    Border,
    Side
)
from openpyxl.utils.dataframe import dataframe_to_rows

from sigem_db import get_db_path


# =====================================================
# OBTENER EMBARQUES / TRANSPORTES
# =====================================================

def obtener_embarques():

    conn = sqlite3.connect(
        get_db_path("logistica")
    )

    query = """
        SELECT
            e.folio_embarque,
            e.folio_hoja_carga,
            e.codigo_transporte,
            e.folio_ruta,
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

            i.tipo_incidencia,
            i.prioridad AS prioridad_incidencia,
            i.estatus AS estatus_incidencia,
            i.descripcion_incidencia,
            i.fecha AS fecha_incidencia

        FROM embarques e

        LEFT JOIN (

            SELECT
                i1.*

            FROM incidencias i1

            INNER JOIN (

                SELECT
                    folio_embarque,
                    MAX(fecha) AS max_fecha

                FROM incidencias

                GROUP BY folio_embarque

            ) ult

            ON i1.folio_embarque = ult.folio_embarque
            AND i1.fecha = ult.max_fecha

        ) i

        ON e.folio_embarque = i.folio_embarque

        ORDER BY e.fecha DESC,
                 e.folio_embarque DESC
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


# =====================================================
# GENERAR DATAFRAME TRANSPORTES
# =====================================================

def generar_df_transportes(df):

    df = df.copy()

    df["codigo_transporte"] = (
        df["codigo_transporte"]
        .fillna("SIN TRANSPORTE")
        .astype(str)
    )

    df["vehiculo"] = (
        df["vehiculo"]
        .fillna("")
        .astype(str)
    )

    df["transporte_display"] = (
        df["codigo_transporte"]
        + " - "
        + df["vehiculo"]
    )

    resumen = (

        df.groupby(
            [
                "transporte_display",
                "codigo_transporte",
                "transportista",
                "vehiculo",
                "placas",
                "operador",
                "ruta",
                "estatus"
            ],
            dropna=False
        )

        .agg(
            embarques=("folio_embarque", "nunique"),
            clientes=("cliente", "nunique"),
            destinos=("destino", "nunique")
        )

        .reset_index()
    )

    return resumen


# =====================================================
# EXPORTAR EXCEL
# =====================================================

def generar_excel_dashboard(
    df_transportes,
    df_detalle,
    total_transportes,
    transito,
    pendientes,
    cumplimiento
):

    wb = Workbook()

    ws = wb.active

    ws.title = "Dashboard transportes"

    azul = PatternFill(
        start_color="1F4E78",
        end_color="1F4E78",
        fill_type="solid"
    )

    gris = PatternFill(
        start_color="D1D5DB",
        end_color="D1D5DB",
        fill_type="solid"
    )

    borde = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin")
    )

    font_blanca = Font(
        color="FFFFFF",
        bold=True
    )

    ws["A1"] = "SIGEM - Dashboard transportes"

    ws["A1"].font = Font(
        bold=True,
        size=16
    )

    ws["A3"] = "Total transportes"
    ws["B3"] = total_transportes

    ws["A4"] = "En tránsito"
    ws["B4"] = transito

    ws["A5"] = "Pendientes"
    ws["B5"] = pendientes

    ws["A6"] = "Cumplimiento"
    ws["B6"] = f"{cumplimiento}%"

    for celda in [
        "A3",
        "A4",
        "A5",
        "A6"
    ]:

        ws[celda].fill = azul
        ws[celda].font = font_blanca
        ws[celda].border = borde

    ws2 = wb.create_sheet(
        title="Transportes"
    )

    for r in dataframe_to_rows(
        df_transportes,
        index=False,
        header=True
    ):

        ws2.append(r)

    for cell in ws2[1]:

        cell.fill = azul
        cell.font = font_blanca
        cell.border = borde

    ws3 = wb.create_sheet(
        title="Detalle embarques"
    )

    for r in dataframe_to_rows(
        df_detalle,
        index=False,
        header=True
    ):

        ws3.append(r)

    for cell in ws3[1]:

        cell.fill = azul
        cell.font = font_blanca
        cell.border = borde

    buffer = BytesIO()

    wb.save(buffer)

    buffer.seek(0)

    return buffer


# =====================================================
# MATRIZ TRANSPORTES
# =====================================================

def pintar_matriz_estatus(df):

    orden_estatus = [
        "Pendiente",
        "En almacén",
        "En patio",
        "Ya salió",
        "En tránsito",
        "Entregado",
        "Cancelado"
    ]

    mapa_colores = {

        "Pendiente": "#6B7280",
        "En almacén": "#7C3AED",
        "En patio": "#F97316",
        "Ya salió": "#EAB308",
        "En tránsito": "#2563EB",
        "Entregado": "#16A34A",
        "Cancelado": "#DC2626"

    }

    df_grafica = df.copy()

    df_grafica["estatus"] = (
        df_grafica["estatus"]
        .fillna("Pendiente")
        .astype(str)
    )

    ancho_grafica = max(
        1300,
        len(df_grafica) * 120
    )

    chart = (

        alt.Chart(df_grafica)

        .mark_rect(
            cornerRadius=5,
            width=75,
            height=28
        )

        .encode(

            x=alt.X(
                "transporte_display:N",
                title="Transportes",
                sort=None,
                axis=alt.Axis(
                    labelAngle=-45,
                    labelLimit=180,
                    grid=True,
                    tickSize=0
                )
            ),

            y=alt.Y(
                "estatus:N",
                sort=orden_estatus,
                title="Estatus",
                axis=alt.Axis(
                    grid=True,
                    tickSize=0
                )
            ),

            color=alt.Color(
                "estatus:N",
                scale=alt.Scale(
                    domain=list(
                        mapa_colores.keys()
                    ),
                    range=list(
                        mapa_colores.values()
                    )
                ),
                legend=None
            ),

            tooltip=[

                alt.Tooltip(
                    "transporte_display:N",
                    title="Transporte"
                ),

                alt.Tooltip(
                    "transportista:N",
                    title="Transportista"
                ),

                alt.Tooltip(
                    "operador:N",
                    title="Operador"
                ),

                alt.Tooltip(
                    "ruta:N",
                    title="Ruta"
                ),

                alt.Tooltip(
                    "embarques:Q",
                    title="Embarques"
                ),

                alt.Tooltip(
                    "estatus:N",
                    title="Estatus"
                )
            ]

        )

        .properties(
            width=ancho_grafica,
            height=520
        )

        .configure_axis(
            grid=True,
            gridColor="#D1D5DB",
            gridDash=[3, 2],
            domain=False,
            labelColor="#374151",
            titleColor="#111827"
        )

        .configure_view(
            stroke="#D1D5DB"
        )

    )

    st.altair_chart(
        chart,
        use_container_width=False
    )


# =====================================================
# APP
# =====================================================

def dashboard_embarques_app():

    st.title("🚛 Dashboard transportes")

    try:

        df = obtener_embarques()

    except Exception as e:

        st.error(
            "❌ Error consultando transportes"
        )

        st.exception(e)

        return

    if df.empty:

        st.warning(
            "No existen transportes registrados."
        )

        return

    st.subheader("🔎 Filtros")

    col1, col2, col3 = st.columns(3)

    with col1:

        filtro_cliente = st.text_input(
            "Cliente"
        )

    with col2:

        filtro_transportista = st.text_input(
            "Transportista"
        )

    with col3:

        filtro_estatus = st.selectbox(
            "Estatus",
            ["Todos"] + sorted(
                df["estatus"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )
        )

    df_filtrado = df.copy()

    if filtro_cliente:

        df_filtrado = df_filtrado[
            df_filtrado["cliente"]
            .astype(str)
            .str.contains(
                filtro_cliente,
                case=False,
                na=False
            )
        ]

    if filtro_transportista:

        df_filtrado = df_filtrado[
            df_filtrado["transportista"]
            .astype(str)
            .str.contains(
                filtro_transportista,
                case=False,
                na=False
            )
        ]

    if filtro_estatus != "Todos":

        df_filtrado = df_filtrado[
            df_filtrado["estatus"]
            .astype(str)
            == filtro_estatus
        ]

    df_transportes = generar_df_transportes(
        df_filtrado
    )

    total_transportes = len(
        df_transportes
    )

    entregados = df_transportes[
        df_transportes["estatus"]
        .astype(str)
        .str.contains(
            "Entregado",
            case=False,
            na=False
        )
    ].shape[0]

    transito = df_transportes[
        df_transportes["estatus"]
        .astype(str)
        .str.contains(
            "tránsito|transito",
            case=False,
            na=False
        )
    ].shape[0]

    pendientes = df_transportes[
        df_transportes["estatus"]
        .astype(str)
        .str.contains(
            "Pendiente",
            case=False,
            na=False
        )
    ].shape[0]

    cumplimiento = (
        round(
            (entregados / total_transportes) * 100,
            1
        )
        if total_transportes > 0 else 0
    )

    st.divider()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "🚛 Transportes",
        total_transportes
    )

    c2.metric(
        "🚚 En tránsito",
        transito
    )

    c3.metric(
        "⏳ Pendientes",
        pendientes
    )

    c4.metric(
        "✅ Cumplimiento",
        f"{cumplimiento}%"
    )

    st.divider()

    st.subheader(
        "🚦 Distribución por transporte"
    )

    pintar_matriz_estatus(
        df_transportes
    )

    st.divider()

    st.subheader(
        "📋 Detalle embarques por transporte"
    )

    st.dataframe(
        df_filtrado,
        use_container_width=True,
        hide_index=True,
        height=420
    )

    st.divider()

    excel_dashboard = generar_excel_dashboard(
        df_transportes,
        df_filtrado,
        total_transportes,
        transito,
        pendientes,
        cumplimiento
    )

    st.download_button(
        label="📥 Exportar dashboard Excel",
        data=excel_dashboard,
        file_name=(
            f"dashboard_transportes_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        ),
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        use_container_width=True
    )


if __name__ == "__main__":

    dashboard_embarques_app()
