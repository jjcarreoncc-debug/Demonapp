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

from sigem_db import get_db_path


# =====================================================
# OBTENER EMBARQUES
# =====================================================

def obtener_embarques():

    conn = sqlite3.connect(
        get_db_path("logistica")
    )

    query = """
        SELECT
            folio_embarque,
            folio_hoja_carga,
            folio_ruta,
            pedido,
            fecha,
            cliente,
            destino,
            transportista,
            vehiculo,
            placas,
            operador,
            ruta,
            estatus
        FROM embarques
        ORDER BY fecha DESC, folio_embarque DESC
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


# =====================================================
# EXPORTAR DASHBOARD EXCEL
# =====================================================

def generar_excel_dashboard(
    df_filtrado,
    total,
    transito,
    pendientes,
    cumplimiento
):

    wb = Workbook()

    ws = wb.active

    ws.title = "Dashboard"

    # =====================================================
    # ESTILOS
    # =====================================================

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

    # =====================================================
    # TITULO
    # =====================================================

    ws["A1"] = "SIGEM - Dashboard embarques"

    ws["A1"].font = Font(
        bold=True,
        size=16
    )

    # =====================================================
    # KPIS
    # =====================================================

    ws["A3"] = "Total embarques"
    ws["B3"] = total

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

    # =====================================================
    # MATRIZ
    # =====================================================

    fila_inicio = 10
    col_inicio = 2

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

        "Pendiente": "9CA3AF",
        "En almacén": "7C3AED",
        "En patio": "F97316",
        "Ya salió": "EAB308",
        "En tránsito": "2563EB",
        "Entregado": "16A34A",
        "Cancelado": "DC2626"

    }

    embarques = (
        df_filtrado["folio_embarque"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    # =====================================================
    # ENCABEZADOS EMBARQUES
    # =====================================================

    for idx, embarque in enumerate(embarques):

        celda = ws.cell(
            row=fila_inicio,
            column=col_inicio + idx
        )

        celda.value = embarque

        celda.fill = gris

        celda.font = Font(
            bold=True
        )

        celda.alignment = Alignment(
            textRotation=45,
            horizontal="center",
            vertical="center"
        )

        celda.border = borde

        ws.column_dimensions[
            celda.column_letter
        ].width = 14

    # =====================================================
    # ESTATUS
    # =====================================================

    for idx_estatus, estatus in enumerate(orden_estatus):

        fila_actual = fila_inicio + 1 + idx_estatus

        celda_estatus = ws.cell(
            row=fila_actual,
            column=1
        )

        celda_estatus.value = estatus

        celda_estatus.fill = gris

        celda_estatus.font = Font(
            bold=True
        )

        celda_estatus.border = borde

        for idx_embarque, embarque in enumerate(embarques):

            celda = ws.cell(
                row=fila_actual,
                column=col_inicio + idx_embarque
            )

            existe = df_filtrado[
                (
                    df_filtrado["folio_embarque"]
                    .astype(str)
                    == embarque
                )
                &
                (
                    df_filtrado["estatus"]
                    .astype(str)
                    == estatus
                )
            ]

            if not existe.empty:

                color = mapa_colores.get(
                    estatus,
                    "D1D5DB"
                )

                celda.fill = PatternFill(
                    start_color=color,
                    end_color=color,
                    fill_type="solid"
                )

            celda.border = borde

    # =====================================================
    # HOJA DETALLE
    # =====================================================

    ws2 = wb.create_sheet(
        title="Detalle embarques"
    )

    for r in dataframe_to_rows(
        df_filtrado,
        index=False,
        header=True
    ):

        ws2.append(r)

    for cell in ws2[1]:

        cell.fill = azul

        cell.font = font_blanca

        cell.border = borde

    # =====================================================
    # BUFFER
    # =====================================================

    buffer = BytesIO()

    wb.save(buffer)

    buffer.seek(0)

    return buffer


# =====================================================
# GRAFICA MATRIZ
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

    df_grafica["embarque"] = (
        df_grafica["folio_embarque"]
        .fillna("")
        .astype(str)
    )

    ancho_grafica = max(
        1300,
        len(df_grafica) * 95
    )

    chart = (
        alt.Chart(df_grafica)
        .mark_rect(
            cornerRadius=5,
            width=62,
            height=26
        )
        .encode(
            x=alt.X(
                "embarque:N",
                title="Número de embarque",
                sort=None,
                axis=alt.Axis(
                    labelAngle=-45
                )
            ),
            y=alt.Y(
                "estatus:N",
                sort=orden_estatus,
                title="Estatus"
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
            )
        )
        .properties(
            width=ancho_grafica,
            height=520
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

    st.title("📊 Dashboard embarques")

    try:

        df = obtener_embarques()

    except Exception as e:

        st.error(
            "❌ Error consultando embarques"
        )

        st.exception(e)

        return

    if df.empty:

        st.warning(
            "No existen embarques registrados."
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

    total = len(df_filtrado)

    entregados = df_filtrado[
        df_filtrado["estatus"]
        .astype(str)
        .str.contains(
            "Entregado",
            case=False,
            na=False
        )
    ].shape[0]

    transito = df_filtrado[
        df_filtrado["estatus"]
        .astype(str)
        .str.contains(
            "tránsito|transito",
            case=False,
            na=False
        )
    ].shape[0]

    pendientes = df_filtrado[
        df_filtrado["estatus"]
        .astype(str)
        .str.contains(
            "Pendiente",
            case=False,
            na=False
        )
    ].shape[0]

    cumplimiento = (
        round(
            (entregados / total) * 100,
            1
        )
        if total > 0 else 0
    )

    st.divider()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "📦 Embarques",
        total
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
        "🚦 Distribución por estatus"
    )

    pintar_matriz_estatus(
        df_filtrado
    )

    st.divider()

    # =====================================================
    # EXPORTAR EXCEL ABAJO
    # =====================================================

    excel_dashboard = generar_excel_dashboard(
        df_filtrado,
        total,
        transito,
        pendientes,
        cumplimiento
    )

    st.download_button(
        label="📥 Exportar dashboard Excel",
        data=excel_dashboard,
        file_name=(
            f"dashboard_embarques_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        ),
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        use_container_width=True
    )
