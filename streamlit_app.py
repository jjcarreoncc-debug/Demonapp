# === DASHBOARD PRO NIVEL DIRECTOR FINAL ===

import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(page_title="Dashboard Ejecutivo", layout="wide")

# -------------------------
# NAV
# -------------------------
if "vista" not in st.session_state:
    st.session_state.vista = "principal"

# -------------------------
# PDF NIVEL DIRECTOR
# -------------------------
def generar_pdf(df_m, df, ventas, ganancia, margen, crecimiento, ratio):

    styles = getSampleStyleSheet()

    titulo = ParagraphStyle(
        'titulo', parent=styles['Heading1'],
        fontSize=22, textColor=colors.black, spaceAfter=20
    )

    subtitulo = ParagraphStyle(
        'subtitulo', parent=styles['Normal'],
        fontSize=14, textColor=colors.grey
    )

    texto = ParagraphStyle(
        'texto', parent=styles['Normal'],
        fontSize=12, spaceAfter=10
    )

    doc = SimpleDocTemplate("reporte_director.pdf")
    story = []

    # PORTADA
    story.append(Paragraph("REPORTE EJECUTIVO", titulo))
    story.append(Paragraph("Análisis estratégico del negocio", subtitulo))
    story.append(Spacer(1, 40))
    story.append(Paragraph("Confidencial", texto))
    story.append(PageBreak())

    # MENSAJE CLAVE
    story.append(Paragraph("Mensaje Clave", titulo))

    if ratio > 0.30:
        mensaje = "Alta volatilidad en el negocio, riesgo operativo elevado."
    elif margen < 30:
        mensaje = "Rentabilidad limitada, presión en costos."
    else:
        mensaje = "Negocio estable con oportunidades de crecimiento."

    story.append(Paragraph(mensaje, texto))
    story.append(PageBreak())

    # KPIs
    story.append(Paragraph("Indicadores Clave", titulo))
    story.append(Paragraph(f"Ventas: ${ventas:,.0f}", texto))
    story.append(Paragraph(f"Ganancia: ${ganancia:,.0f}", texto))
    story.append(Paragraph(f"Margen: {margen:.1f}%", texto))
    story.append(Paragraph(f"Crecimiento: {crecimiento:.1f}%", texto))
    story.append(PageBreak())

    # TENDENCIA
    plt.figure(figsize=(10,5))
    plt.plot(df_m["Periodo"], df_m["Ventas"], label="Ventas")
    plt.plot(df_m["Periodo"], df_m["Ganancia"], label="Ganancia")
    plt.legend()
    plt.xticks(rotation=45)
    plt.title("Tendencia del negocio")
    plt.tight_layout()
    plt.savefig("tendencia.png")
    plt.close()

    story.append(Paragraph("Evolución del negocio", titulo))
    story.append(Image("tendencia.png", width=520, height=300))
    story.append(PageBreak())

    # RESPONSABLES
    if "Nombre" in df.columns:
        df_nom = df.groupby("Nombre")["Ventas"].sum().sort_values(ascending=False).head(5)

        plt.figure(figsize=(10,5))
        df_nom.plot(kind='bar')
        plt.xticks(rotation=45)
        plt.title("Top responsables")
        plt.tight_layout()
        plt.savefig("resp.png")
        plt.close()

        story.append(Paragraph("Responsables Clave", titulo))
        story.append(Image("resp.png", width=520, height=300))
        story.append(PageBreak())

    # REGIONES
    if "Region" in df.columns:
        df_reg = df.groupby("Region")["Ventas"].sum().sort_values(ascending=False)

        plt.figure(figsize=(10,5))
        df_reg.plot(kind='bar')
        plt.xticks(rotation=45)
        plt.title("Impacto por región")
        plt.tight_layout()
        plt.savefig("reg.png")
        plt.close()

        story.append(Paragraph("Distribución Geográfica", titulo))
        story.append(Image("reg.png", width=520, height=300))
        story.append(PageBreak())

    # RIESGO
    story.append(Paragraph("Riesgo del Negocio", titulo))

    if ratio > 0.30:
        riesgo = "Alto riesgo por inestabilidad."
    elif ratio > 0.15:
        riesgo = "Riesgo moderado."
    else:
        riesgo = "Riesgo controlado."

    story.append(Paragraph(riesgo, texto))
    story.append(PageBreak())

    # RECOMENDACIÓN
    story.append(Paragraph("Recomendación Estratégica", titulo))

    if ratio > 0.30:
        rec = "Implementar control inmediato y seguimiento semanal."
    elif margen < 30:
        rec = "Optimizar estructura de costos."
    else:
        rec = "Escalar estrategia actual."

    story.append(Paragraph(rec, texto))

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
    st.sidebar.header("Filtros")

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

        st.title("Dashboard Ejecutivo")

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

        if col1.button("Volatilidad"):
            st.session_state.vista = "volatilidad"
        if col2.button("Responsables"):
            st.session_state.vista = "responsables"
        if col3.button("Causas"):
            st.session_state.vista = "causas"
        if col4.button("Reporte"):
            st.session_state.vista = "reporte"

    elif st.session_state.vista == "volatilidad":

        st.title("Volatilidad")

        if st.button("Volver"):
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

        st.title("Responsables")

        if st.button("Volver"):
            st.session_state.vista = "principal"

        df_nom = df.groupby(["Periodo", "Nombre"])["Ventas"].sum().reset_index()
        fig = px.line(df_nom, x="Periodo", y="Ventas", color="Nombre")
        st.plotly_chart(fig, use_container_width=True)

    elif st.session_state.vista == "causas":

        st.title("Causas")

        if st.button("Volver"):
            st.session_state.vista = "principal"

        df_reg = df.groupby(["Periodo", "Region"])["Ventas"].sum().reset_index()
        fig = px.line(df_reg, x="Periodo", y="Ventas", color="Region")
        st.plotly_chart(fig, use_container_width=True)

    elif st.session_state.vista == "reporte":

        st.title("Reporte Ejecutivo")

        if st.button("Volver"):
            st.session_state.vista = "principal"

        ventas = df["Ventas"].sum()
        ganancia = df["Ganancia"].sum()
        margen = (ganancia / ventas * 100) if ventas != 0 else 0
        crecimiento = df_m["Ventas"].pct_change().mean() * 100

        if st.button("Descargar PDF"):

            media = df_m["Ventas"].mean()
            vol = df_m["Ventas"].std()
            ratio = vol / media if media != 0 else 0

            generar_pdf(df_m, df, ventas, ganancia, margen, crecimiento, ratio)

            with open("reporte_director.pdf", "rb") as f:
                st.download_button("Descargar reporte", f, "reporte_director.pdf")

else:
    st.info("Sube archivo Excel")
