# === DASHBOARD PRO MODO CONSULTORA FINAL ===

import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import os

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(page_title="Dashboard Ejecutivo PRO", layout="wide")

# -------------------------
# NAV
# -------------------------
if "vista" not in st.session_state:
    st.session_state.vista = "principal"

# -------------------------
# PDF MODO CONSULTORA
# -------------------------
def generar_pdf(df_m, df, ventas, ganancia, margen, crecimiento, ratio):

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate("reporte_consultora.pdf")
    story = []

    # PORTADA
    story.append(Paragraph("Reporte Ejecutivo", styles['Title']))
    story.append(Spacer(1, 30))
    story.append(Paragraph("Análisis estratégico de ventas", styles['Normal']))
    story.append(PageBreak())

    # KPIs
    story.append(Paragraph("Resumen Ejecutivo", styles['Heading1']))
    story.append(Paragraph(f"Ventas: ${ventas:,.0f}", styles['Heading2']))
    story.append(Paragraph(f"Ganancia: ${ganancia:,.0f}", styles['Heading2']))
    story.append(Paragraph(f"Margen: {margen:.1f}%", styles['Heading2']))
    story.append(Paragraph(f"Crecimiento: {crecimiento:.1f}%", styles['Heading2']))
    story.append(PageBreak())

    # TENDENCIA
    plt.figure(figsize=(10,5))
    plt.plot(df_m["Periodo"], df_m["Ventas"], marker='o', label="Ventas")
    plt.plot(df_m["Periodo"], df_m["Ganancia"], marker='o', label="Ganancia")
    plt.xticks(rotation=45)
    plt.legend()
    plt.title("Tendencia Ventas vs Ganancia")
    plt.tight_layout()
    plt.savefig("tendencia.png")
    plt.close()

    story.append(Paragraph("Tendencia General", styles['Heading1']))
    story.append(Image("tendencia.png", width=520, height=300))
    story.append(PageBreak())

    # CRECIMIENTO
    df_m["Crecimiento"] = df_m["Ventas"].pct_change()

    plt.figure(figsize=(10,4))
    plt.plot(df_m["Periodo"], df_m["Crecimiento"], marker='o')
    plt.axhline(0)
    plt.xticks(rotation=45)
    plt.title("Variación de Crecimiento")
    plt.tight_layout()
    plt.savefig("crecimiento.png")
    plt.close()

    story.append(Paragraph("Crecimiento", styles['Heading1']))
    story.append(Image("crecimiento.png", width=520, height=300))
    story.append(PageBreak())

    # RESPONSABLES
    if "Nombre" in df.columns:
        df_nom = df.groupby("Nombre")["Ventas"].sum().sort_values(ascending=False).head(10)

        plt.figure(figsize=(10,5))
        df_nom.plot(kind='bar')
        plt.xticks(rotation=45)
        plt.title("Top Responsables")
        plt.tight_layout()
        plt.savefig("responsables.png")
        plt.close()

        story.append(Paragraph("Responsables Clave", styles['Heading1']))
        story.append(Image("responsables.png", width=520, height=300))
        story.append(PageBreak())

    # REGIONES
    if "Region" in df.columns:
        df_reg = df.groupby("Region")["Ventas"].sum().sort_values(ascending=False)

        plt.figure(figsize=(10,5))
        df_reg.plot(kind='bar')
        plt.xticks(rotation=45)
        plt.title("Impacto por Región")
        plt.tight_layout()
        plt.savefig("regiones.png")
        plt.close()

        story.append(Paragraph("Impacto por Región", styles['Heading1']))
        story.append(Image("regiones.png", width=520, height=300))
        story.append(PageBreak())

    # VOLATILIDAD
    plt.figure(figsize=(10,4))
    plt.plot(df_m["Periodo"], df_m["Ventas"])
    plt.xticks(rotation=45)
    plt.title("Volatilidad")
    plt.tight_layout()
    plt.savefig("volatilidad.png")
    plt.close()

    story.append(Paragraph("Volatilidad", styles['Heading1']))
    story.append(Image("volatilidad.png", width=520, height=300))

    if ratio > 0.30:
        estado = "Alta inestabilidad"
    elif ratio > 0.15:
        estado = "Variabilidad moderada"
    else:
        estado = "Estable"

    story.append(Paragraph(f"Estado: {estado}", styles['Normal']))
    story.append(PageBreak())

    # INSIGHTS
    story.append(Paragraph("Insights Automáticos", styles['Heading1']))

    insights = []
    if ratio > 0.30:
        insights.append("Alta volatilidad detectada")
    if margen < 30:
        insights.append("Margen bajo")
    if crecimiento < 0:
        insights.append("Crecimiento negativo")
    if not insights:
        insights.append("Comportamiento estable")

    for i in insights:
        story.append(Paragraph(f"- {i}", styles['Normal']))

    story.append(PageBreak())

    # CONCLUSIÓN
    story.append(Paragraph("Conclusión", styles['Heading1']))

    if ratio > 0.30:
        conclusion = "Se requiere estabilización inmediata."
    elif margen < 30:
        conclusion = "Optimizar costos."
    else:
        conclusion = "Negocio saludable."

    story.append(Paragraph(conclusion, styles['Normal']))

    doc.build(story)

# -------------------------
# DATA
# -------------------------
archivo = st.file_uploader("Sube tu Excel", type=["xlsx"])

if archivo:

    df = pd.read_excel(archivo)
    df.columns = df.columns.str.strip()

    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df = df.dropna(subset=["Fecha"])

    df["Ganancia"] = df["Ventas"] - df["Costos"]
    df["Periodo"] = df["Fecha"].dt.to_period("M").astype(str)

    # FILTROS
    st.sidebar.header("🔎 Filtros")

    if "Pais" in df.columns:
        pais = st.sidebar.multiselect("País", df["Pais"].unique(), default=df["Pais"].unique())
        df = df[df["Pais"].isin(pais)]

    if "Region" in df.columns:
        reg = st.sidebar.multiselect("Región", df["Region"].unique(), default=df["Region"].unique())
        df = df[df["Region"].isin(reg)]

    if "Nombre" in df.columns:
        nom = st.sidebar.multiselect("Nombre", df["Nombre"].unique(), default=df["Nombre"].unique())
        df = df[df["Nombre"].isin(nom)]

    if df.empty:
        st.warning("Sin datos")
        st.stop()

    df_m = df.groupby("Periodo")[["Ventas", "Ganancia"]].sum().reset_index()

    # PRINCIPAL
    if st.session_state.vista == "principal":

        st.title("📊 Dashboard Ejecutivo")

        ventas = df["Ventas"].sum()
        ganancia = df["Ganancia"].sum()
        margen = (ganancia / ventas * 100) if ventas != 0 else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("Ventas", f"${ventas:,.0f}")
        c2.metric("Ganancia", f"${ganancia:,.0f}")
        c3.metric("Margen", f"{margen:.1f}%")

        fig = px.line(df_m, x="Periodo", y=["Ventas", "Ganancia"], markers=True)
        st.plotly_chart(fig, use_container_width=True)

        col1, col2, col3, col4 = st.columns(4)

        if col1.button("🚦 Volatilidad"):
            st.session_state.vista = "volatilidad"
        if col2.button("👤 Responsables"):
            st.session_state.vista = "responsables"
        if col3.button("🔎 Causas"):
            st.session_state.vista = "causas"
        if col4.button("📄 Reporte"):
            st.session_state.vista = "reporte"

    elif st.session_state.vista == "volatilidad":

        st.title("🚦 Volatilidad")

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        media = df_m["Ventas"].mean()
        vol = df_m["Ventas"].std()
        ratio = vol / media if media != 0 else 0

        if ratio > 0.30:
            st.error("Alta inestabilidad")
        elif ratio > 0.15:
            st.warning("Variabilidad moderada")
        else:
            st.success("Estable")

        st.line_chart(df_m.set_index("Periodo")["Ventas"])

    elif st.session_state.vista == "responsables":

        st.title("👤 Responsables")

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        df_nom = df.groupby(["Periodo", "Nombre"])["Ventas"].sum().reset_index()
        fig = px.line(df_nom, x="Periodo", y="Ventas", color="Nombre")
        st.plotly_chart(fig, use_container_width=True)

    elif st.session_state.vista == "causas":

        st.title("🔎 Causas")

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        df_reg = df.groupby(["Periodo", "Region"])["Ventas"].sum().reset_index()
        fig = px.line(df_reg, x="Periodo", y="Ventas", color="Region")
        st.plotly_chart(fig, use_container_width=True)

    elif st.session_state.vista == "reporte":

        st.title("📄 Reporte Ejecutivo")

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        ventas = df["Ventas"].sum()
        ganancia = df["Ganancia"].sum()
        margen = (ganancia / ventas * 100) if ventas != 0 else 0
        crecimiento = df_m["Ventas"].pct_change().mean() * 100

        if st.button("📄 Descargar PDF Consultora"):

            media = df_m["Ventas"].mean()
            vol = df_m["Ventas"].std()
            ratio = vol / media if media != 0 else 0

            generar_pdf(df_m, df, ventas, ganancia, margen, crecimiento, ratio)

            with open("reporte_consultora.pdf", "rb") as f:
                st.download_button("Descargar", f, "reporte_consultora.pdf")

else:
    st.info("Sube archivo Excel")
