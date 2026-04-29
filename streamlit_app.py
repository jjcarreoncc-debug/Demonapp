# === VERSION ESTABLE PDF + PPT (FUNCIONANDO REAL) ===

import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import os

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet

from pptx import Presentation
from pptx.util import Inches

st.set_page_config(page_title="Dashboard Ejecutivo", layout="wide")

# =========================
# FUNCION GRAFICAS (CLAVE)
# =========================
def guardar_img(nombre, plot_func):
    plt.figure(figsize=(10,5))
    plt.rcParams["figure.dpi"] = 120
    plot_func()
    plt.tight_layout()
    plt.savefig(nombre)
    plt.close()
    return nombre

# =========================
# PDF
# =========================
def generar_pdf(df_m, df, ventas, ganancia, margen, crecimiento, ratio):

    doc = SimpleDocTemplate("reporte_final.pdf")
    styles = getSampleStyleSheet()
    story = []

    # PORTADA
    story.append(Paragraph("REPORTE EJECUTIVO", styles['Title']))
    story.append(Spacer(1, 20))
    story.append(Paragraph("Análisis del negocio", styles['Normal']))
    story.append(PageBreak())

    # KPIs
    story.append(Paragraph("KPIs", styles['Heading1']))
    story.append(Paragraph(f"Ventas: ${ventas:,.0f}", styles['Normal']))
    story.append(Paragraph(f"Ganancia: ${ganancia:,.0f}", styles['Normal']))
    story.append(Paragraph(f"Margen: {margen:.1f}%", styles['Normal']))
    story.append(PageBreak())

    # GRAFICA
    img1 = guardar_img("temp_tendencia.png", lambda: (
        plt.plot(df_m["Periodo"], df_m["Ventas"], label="Ventas"),
        plt.plot(df_m["Periodo"], df_m["Ganancia"], label="Ganancia"),
        plt.legend(),
        plt.xticks(rotation=45),
        plt.title("Tendencia")
    ))

    story.append(Paragraph("Tendencia", styles['Heading1']))
    story.append(Image(img1, width=500, height=300))
    story.append(PageBreak())

    # FINAL
    story.append(Paragraph("Conclusión", styles['Heading1']))
    story.append(Paragraph("Seguimiento semanal recomendado.", styles['Normal']))

    doc.build(story)

    if os.path.exists("temp_tendencia.png"):
        os.remove("temp_tendencia.png")

# =========================
# POWERPOINT
# =========================
def generar_ppt(df_m, df, ventas, ganancia, margen, crecimiento, ratio):

    prs = Presentation()

    # PORTADA
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = "Reporte Ejecutivo"
    slide.placeholders[1].text = "Análisis del negocio"

    # KPIs
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "KPIs"
    slide.placeholders[1].text = f"""
Ventas: ${ventas:,.0f}
Ganancia: ${ganancia:,.0f}
Margen: {margen:.1f}%
"""

    # GRAFICA
    img = guardar_img("temp_ppt.png", lambda: (
        plt.plot(df_m["Periodo"], df_m["Ventas"]),
        plt.plot(df_m["Periodo"], df_m["Ganancia"])
    ))

    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.shapes.title.text = "Tendencia"
    slide.shapes.add_picture(img, Inches(1), Inches(2), width=Inches(8))

    prs.save("reporte.pptx")

    if os.path.exists("temp_ppt.png"):
        os.remove("temp_ppt.png")

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

    df_m = df.groupby("Periodo")[["Ventas", "Ganancia"]].sum().reset_index()

    ventas = df["Ventas"].sum()
    ganancia = df["Ganancia"].sum()
    margen = (ganancia / ventas * 100) if ventas != 0 else 0
    crecimiento = df_m["Ventas"].pct_change().mean() * 100

    st.title("📊 Dashboard Ejecutivo")

    st.metric("Ventas", f"${ventas:,.0f}")
    st.metric("Ganancia", f"${ganancia:,.0f}")
    st.metric("Margen", f"{margen:.1f}%")

    fig = px.line(df_m, x="Periodo", y=["Ventas", "Ganancia"])
    st.plotly_chart(fig, use_container_width=True)

    # BOTONES
    if st.button("📄 Generar PDF"):
        generar_pdf(df_m, df, ventas, ganancia, margen, crecimiento, 0)
        with open("reporte_final.pdf", "rb") as f:
            st.download_button("Descargar PDF", f, "reporte_final.pdf")

    if st.button("📊 Generar PowerPoint"):
        generar_ppt(df_m, df, ventas, ganancia, margen, crecimiento, 0)
        with open("reporte.pptx", "rb") as f:
            st.download_button("Descargar PPT", f, "reporte.pptx")

else:
    st.info("Sube un archivo Excel")
