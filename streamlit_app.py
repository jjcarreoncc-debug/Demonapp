# === DASHBOARD FINAL NIVEL DIRECTOR (FIX DEFINITIVO) ===

import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from io import BytesIO

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet

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
# PDF (VERSIÓN ESTABLE)
# -------------------------
def generar_pdf(df_m, df, ventas, ganancia, margen, crecimiento, ratio):

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate("reporte_director.pdf")
    story = []

    # 🔥 FUNCIÓN CORRECTA (BYTESIO)
    def fig_to_img(plot_func):
        buffer = BytesIO()
        plt.figure(figsize=(10,5))
        plt.rcParams["figure.dpi"] = 120  # mejora calidad
        plot_func()
        plt.tight_layout()
        plt.savefig(buffer, format="png")
        plt.close()
        buffer.seek(0)
        return buffer

    # -------------------------
    # PORTADA
    # -------------------------
    story.append(Paragraph("REPORTE EJECUTIVO", styles['Title']))
    story.append(Spacer(1, 20))
    story.append(Paragraph("Análisis estratégico del negocio", styles['Normal']))
    story.append(PageBreak())

    # -------------------------
    # KPIs
    # -------------------------
    story.append(Paragraph("Indicadores Clave", styles['Heading1']))
    story.append(Paragraph(f"Ventas: ${ventas:,.0f}", styles['Normal']))
    story.append(Paragraph(f"Ganancia: ${ganancia:,.0f}", styles['Normal']))
    story.append(Paragraph(f"Margen: {margen:.1f}%", styles['Normal']))
    story.append(Paragraph(f"Crecimiento: {crecimiento:.1f}%", styles['Normal']))
    story.append(PageBreak())

    # -------------------------
    # TENDENCIA
    # -------------------------
    img = fig_to_img(lambda: (
        plt.plot(df_m["Periodo"], df_m["Ventas"], label="Ventas"),
        plt.plot(df_m["Periodo"], df_m["Ganancia"], label="Ganancia"),
        plt.legend(),
        plt.xticks(rotation=45),
        plt.title("Tendencia del negocio")
    ))

    story.append(Paragraph("Tendencia del negocio", styles['Heading1']))
    story.append(Image(img, width=500, height=300))
    story.append(PageBreak())

    # -------------------------
    # RESPONSABLES
    # -------------------------
    if "Nombre" in df.columns:
        df_nom = df.groupby("Nombre")["Ventas"].sum().sort_values(ascending=False).head(5)

        img = fig_to_img(lambda: (
            df_nom.plot(kind='bar'),
            plt.xticks(rotation=45),
            plt.title("Top responsables")
        ))

        story.append(Paragraph("Responsables", styles['Heading1']))
        story.append(Image(img, width=500, height=300))
        story.append(PageBreak())

    # -------------------------
    # REGIONES
    # -------------------------
    if "Region" in df.columns:
        df_reg = df.groupby("Region")["Ventas"].sum()

        img = fig_to_img(lambda: (
            df_reg.plot(kind='bar'),
            plt.xticks(rotation=45),
            plt.title("Impacto por región")
        ))

        story.append(Paragraph("Regiones", styles['Heading1']))
        story.append(Image(img, width=500, height=300))
        story.append(PageBreak())

    # -------------------------
    # VOLATILIDAD
    # -------------------------
    story.append(Paragraph("Volatilidad", styles['Heading1']))

    if ratio > 0.30:
        estado = "Alta inestabilidad"
    elif ratio > 0.15:
        estado = "Variabilidad moderada"
    else:
        estado = "Estable"

    story.append(Paragraph(f"Estado: {estado}", styles['Normal']))
    story.append(PageBreak())

    # -------------------------
    # CONCLUSIÓN
    # -------------------------
    story.append(Paragraph("Conclusión", styles['Heading1']))
    story.append(Paragraph(
        "Se recomienda monitoreo continuo y optimización del negocio.",
        styles['Normal']
    ))

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

    # -------------------------
    # FILTROS
    # -------------------------
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

    # -------------------------
    # PRINCIPAL
    # -------------------------
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

    # -------------------------
    # VOLATILIDAD
    # -------------------------
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

    # -------------------------
    # RESPONSABLES
    # -------------------------
    elif st.session_state.vista == "responsables":

        st.title("👤 Responsables")

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        df_nom = df.groupby(["Periodo", "Nombre"])["Ventas"].sum().reset_index()
        fig = px.line(df_nom, x="Periodo", y="Ventas", color="Nombre")
        st.plotly_chart(fig, use_container_width=True)

    # -------------------------
    # CAUSAS
    # -------------------------
    elif st.session_state.vista == "causas":

        st.title("🔎 Causas")

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        df_reg = df.groupby(["Periodo", "Region"])["Ventas"].sum().reset_index()
        fig = px.line(df_reg, x="Periodo", y="Ventas", color="Region")
        st.plotly_chart(fig, use_container_width=True)

    # -------------------------
    # REPORTE
    # -------------------------
    elif st.session_state.vista == "reporte":

        st.title("📄 Reporte Ejecutivo")

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        ventas = df["Ventas"].sum()
        ganancia = df["Ganancia"].sum()
        margen = (ganancia / ventas * 100) if ventas != 0 else 0
        crecimiento = df_m["Ventas"].pct_change().mean() * 100

        if st.button("📄 Descargar PDF"):

            media = df_m["Ventas"].mean()
            vol = df_m["Ventas"].std()
            ratio = vol / media if media != 0 else 0

            generar_pdf(df_m, df, ventas, ganancia, margen, crecimiento, ratio)

            with open("reporte_director.pdf", "rb") as f:
                st.download_button("Descargar reporte", f, "reporte_director.pdf")

else:
    st.info("📂 Sube un archivo Excel")
