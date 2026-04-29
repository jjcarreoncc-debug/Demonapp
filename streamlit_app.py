# === VERSION COMPLETA (MISMA APP + FIX SOLO PDF/PPT EN BUFFER) ===

import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet

from pptx import Presentation
from pptx.util import Inches

from io import BytesIO

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(page_title="Dashboard Ejecutivo", layout="wide")

if "vista" not in st.session_state:
    st.session_state.vista = "principal"

# =========================
# PDF (BUFFER - FIX)
# =========================
def generar_pdf(df_m, ventas, ganancia, margen, ratio):

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    story = []

    # PORTADA
    story.append(Paragraph("REPORTE EJECUTIVO", styles['Title']))
    story.append(Spacer(1, 20))
    story.append(PageBreak())

    # KPIs
    story.append(Paragraph("KPIs", styles['Heading1']))
    story.append(Paragraph(f"Ventas: ${ventas:,.0f}", styles['Normal']))
    story.append(Paragraph(f"Ganancia: ${ganancia:,.0f}", styles['Normal']))
    story.append(Paragraph(f"Margen: {margen:.1f}%", styles['Normal']))
    story.append(PageBreak())

    # GRAFICA EN MEMORIA
    img_stream = BytesIO()
    plt.figure(figsize=(10,5))
    plt.plot(df_m["Periodo"], df_m["Ventas"], marker="o", label="Ventas")
    plt.plot(df_m["Periodo"], df_m["Ganancia"], marker="o", label="Ganancia")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(img_stream, format="png")
    plt.close()
    img_stream.seek(0)

    story.append(Paragraph("Tendencia", styles['Heading1']))
    story.append(Image(img_stream, width=450, height=250))
    story.append(PageBreak())

    # VOLATILIDAD
    estado = "Estable"
    if ratio > 0.30:
        estado = "Alta volatilidad"
    elif ratio > 0.15:
        estado = "Volatilidad media"

    story.append(Paragraph("Volatilidad", styles['Heading1']))
    story.append(Paragraph(estado, styles['Normal']))

    doc.build(story)
    buffer.seek(0)

    return buffer

# =========================
# PPT (BUFFER - FIX)
# =========================
def generar_ppt(df_m, ventas, ganancia, margen):

    prs = Presentation()

    # SLIDE 1
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = "Reporte Ejecutivo"
    slide.placeholders[1].text = "Análisis del negocio"

    # SLIDE 2
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "KPIs"
    slide.placeholders[1].text = f"""
Ventas: ${ventas:,.0f}
Ganancia: ${ganancia:,.0f}
Margen: {margen:.1f}%
"""

    # GRAFICA EN MEMORIA
    img_stream = BytesIO()
    plt.figure(figsize=(10,5))
    plt.plot(df_m["Periodo"], df_m["Ventas"], marker="o")
    plt.plot(df_m["Periodo"], df_m["Ganancia"], marker="o")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(img_stream, format="png")
    plt.close()
    img_stream.seek(0)

    # SLIDE 3
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.shapes.title.text = "Tendencia"
    slide.shapes.add_picture(img_stream, Inches(1), Inches(2), width=Inches(8))

    # EXPORTAR
    ppt_buffer = BytesIO()
    prs.save(ppt_buffer)
    ppt_buffer.seek(0)

    return ppt_buffer

# =========================
# APP
# =========================
archivo = st.file_uploader("Sube tu Excel", type=["xlsx"])

if archivo:

    df = pd.read_excel(archivo)
    df.columns = df.columns.str.strip()

    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df = df.dropna(subset=["Fecha"])

    df["Ganancia"] = df["Ventas"] - df["Costos"]
    df["Periodo"] = df["Fecha"].dt.to_period("M").astype(str)

    # FILTROS
    st.sidebar.header("Filtros")

    rango = st.sidebar.date_input("Fecha", [df["Fecha"].min(), df["Fecha"].max()])
    if len(rango) == 2:
        df = df[(df["Fecha"] >= pd.to_datetime(rango[0])) &
                (df["Fecha"] <= pd.to_datetime(rango[1]))]

    if "Pais" in df.columns:
        pais = st.sidebar.multiselect("País", df["Pais"].unique(), df["Pais"].unique())
        df = df[df["Pais"].isin(pais)]

    if "Region" in df.columns:
        reg = st.sidebar.multiselect("Región", df["Region"].unique(), df["Region"].unique())
        df = df[df["Region"].isin(reg)]

    if "Nombre" in df.columns:
        nom = st.sidebar.multiselect("Nombre", df["Nombre"].unique(), df["Nombre"].unique())
        df = df[df["Nombre"].isin(nom)]

    if df.empty:
        st.warning("Sin datos")
        st.stop()

    # CALCULOS
    df_m = df.groupby("Periodo")[["Ventas","Ganancia"]].sum().reset_index()

    ventas = df["Ventas"].sum()
    ganancia = df["Ganancia"].sum()
    margen = (ganancia / ventas * 100) if ventas != 0 else 0

    media = df_m["Ventas"].mean()
    vol = df_m["Ventas"].std()
    ratio = vol / media if media != 0 else 0

    # DASHBOARD
    st.title("📊 Dashboard Ejecutivo")

    c1, c2, c3 = st.columns(3)
    c1.metric("Ventas", f"${ventas:,.0f}")
    c2.metric("Ganancia", f"${ganancia:,.0f}")
    c3.metric("Margen", f"{margen:.1f}%")

    fig = px.line(df_m, x="Periodo", y=["Ventas","Ganancia"], markers=True)
    st.plotly_chart(fig, use_container_width=True)

    # VOLATILIDAD
    st.subheader("🚦 Volatilidad")

    if ratio > 0.30:
        st.error("🔴 Alta volatilidad")
    elif ratio > 0.15:
        st.warning("🟡 Volatilidad media")
    else:
        st.success("🟢 Estable")

    # BOTONES
    col1, col2 = st.columns(2)

    if col1.button("📄 Generar PDF"):
        pdf_file = generar_pdf(df_m, ventas, ganancia, margen, ratio)

        st.download_button(
            label="Descargar PDF",
            data=pdf_file,
            file_name="reporte_final.pdf",
            mime="application/pdf"
        )

    if col2.button("📊 Generar PPT"):
        ppt_file = generar_ppt(df_m, ventas, ganancia, margen)

        st.download_button(
            label="Descargar PPT",
            data=ppt_file,
            file_name="reporte_final.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )

else:
    st.info("📂 Sube un archivo Excel")
