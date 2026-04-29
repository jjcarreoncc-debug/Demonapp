# === DASHBOARD PRO FULL + PDF ESTABLE ===

import streamlit as st
import pandas as pd
import plotly.express as px
import os

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="Dashboard Ejecutivo PRO", layout="wide")

# -------------------------
# NAV
# -------------------------
if "vista" not in st.session_state:
    st.session_state.vista = "principal"

# -------------------------
# PDF
# -------------------------
def generar_pdf(fig, ventas, ganancia, margen, crecimiento, max_mes, min_mes, ratio):

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate("reporte.pdf")
    story = []

    # Intentar guardar gráfica
    try:
        fig.write_image("grafica.png")
        imagen_ok = True
    except:
        imagen_ok = False

    # PORTADA
    story.append(Paragraph("Reporte Ejecutivo", styles['Title']))
    story.append(PageBreak())

    # RESUMEN
    story.append(Paragraph("Resumen Ejecutivo", styles['Heading1']))
    story.append(Paragraph(f"Ventas: ${ventas:,.0f}", styles['Normal']))
    story.append(Paragraph(f"Ganancia: ${ganancia:,.0f}", styles['Normal']))
    story.append(Paragraph(f"Margen: {margen:.1f}%", styles['Normal']))
    story.append(Paragraph(f"Crecimiento: {crecimiento:.1f}%", styles['Normal']))
    story.append(Spacer(1, 20))

    if imagen_ok and os.path.exists("grafica.png"):
        story.append(Image("grafica.png", width=500, height=300))
    else:
        story.append(Paragraph("Gráfica no disponible", styles['Normal']))

    story.append(PageBreak())

    # VOLATILIDAD
    story.append(Paragraph("Volatilidad", styles['Heading1']))

    if ratio > 0.30:
        estado = "Alta inestabilidad"
    elif ratio > 0.15:
        estado = "Variabilidad moderada"
    else:
        estado = "Estable"

    story.append(Paragraph(f"Estado: {estado}", styles['Normal']))
    story.append(PageBreak())

    # CONCLUSIÓN
    story.append(Paragraph("Conclusión", styles['Heading1']))
    story.append(Paragraph("Enfocar acciones en áreas con mayor variabilidad.", styles['Normal']))

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
    st.sidebar.header("🔎 Filtros")

    df_f = df.copy()

    if "Pais" in df.columns:
        pais = st.sidebar.multiselect("País", df["Pais"].unique(), default=df["Pais"].unique())
        df_f = df_f[df_f["Pais"].isin(pais)]

    if "Region" in df.columns:
        reg = st.sidebar.multiselect("Región", df_f["Region"].unique(), default=df_f["Region"].unique())
        df_f = df_f[df_f["Region"].isin(reg)]

    if "Nombre" in df.columns:
        nom = st.sidebar.multiselect("Nombre", df_f["Nombre"].unique(), default=df_f["Nombre"].unique())
        df_f = df_f[df_f["Nombre"].isin(nom)]

    df = df_f

    if df.empty:
        st.warning("Sin datos")
        st.stop()

    df_m = df.groupby("Periodo")[["Ventas", "Ganancia"]].sum().reset_index()

    # =========================
    # PRINCIPAL
    # =========================
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

    # =========================
    # VOLATILIDAD
    # =========================
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

    # =========================
    # RESPONSABLES
    # =========================
    elif st.session_state.vista == "responsables":

        st.title("👤 Responsables")

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        df_nom = df.groupby(["Periodo", "Nombre"])["Ventas"].sum().reset_index()

        fig = px.line(df_nom, x="Periodo", y="Ventas", color="Nombre")
        st.plotly_chart(fig, use_container_width=True)

    # =========================
    # CAUSAS
    # =========================
    elif st.session_state.vista == "causas":

        st.title("🔎 Causas")

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        df_reg = df.groupby(["Periodo", "Region"])["Ventas"].sum().reset_index()

        fig = px.line(df_reg, x="Periodo", y="Ventas", color="Region")
        st.plotly_chart(fig, use_container_width=True)

    # =========================
    # REPORTE
    # =========================
    elif st.session_state.vista == "reporte":

        st.title("📄 Reporte Ejecutivo")

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        ventas = df["Ventas"].sum()
        ganancia = df["Ganancia"].sum()
        margen = (ganancia / ventas * 100) if ventas != 0 else 0
        crecimiento = df_m["Ventas"].pct_change().mean() * 100

        max_mes = df_m.loc[df_m["Ventas"].idxmax()]
        min_mes = df_m.loc[df_m["Ventas"].idxmin()]

        fig = px.line(df_m, x="Periodo", y=["Ventas", "Ganancia"], markers=True)

        if st.button("📄 Descargar PDF"):

            media = df_m["Ventas"].mean()
            vol = df_m["Ventas"].std()
            ratio = vol / media if media != 0 else 0

            generar_pdf(
                fig,
                ventas,
                ganancia,
                margen,
                crecimiento,
                max_mes,
                min_mes,
                ratio
            )

            with open("reporte.pdf", "rb") as f:
                st.download_button("Descargar", f, "reporte.pdf")
