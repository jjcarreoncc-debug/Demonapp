# === DASHBOARD PRO + MODO REPORTE ===

import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(page_title="Dashboard Ejecutivo PRO", layout="wide")

# -------------------------
# ESTILO
# -------------------------
st.markdown("""
<style>
body {background-color: #f7f9fb;}
.block-container {padding-top: 1.5rem;}
div[data-testid="stMetric"] {
    background-color: white;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# NAV
# -------------------------
if "vista" not in st.session_state:
    st.session_state.vista = "principal"

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
    # 🏠 PRINCIPAL
    # =========================
    if st.session_state.vista == "principal":

        st.title("📊 Dashboard Ejecutivo")

        ventas = df["Ventas"].sum()
        ganancia = df["Ganancia"].sum()
        margen = (ganancia / ventas * 100) if ventas != 0 else 0

        st.markdown("### 📌 Indicadores Clave")
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Ventas", f"${ventas:,.0f}")
        c2.metric("📈 Ganancia", f"${ganancia:,.0f}")
        c3.metric("📊 Margen", f"{margen:.1f}%")

        fig = px.line(df_m, x="Periodo", y=["Ventas", "Ganancia"], markers=True)
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", hovermode="x unified")
        fig.update_traces(line=dict(width=3))

        # Anotación último punto
        fig.add_annotation(
            x=df_m["Periodo"].iloc[-1],
            y=df_m["Ventas"].iloc[-1],
            text="Último valor",
            showarrow=True
        )

        st.plotly_chart(fig, use_container_width=True)

        # Navegación
        st.markdown("## 📊 Explorar análisis")

        col1, col2, col3, col4 = st.columns(4)

        if col1.button("🚦 Volatilidad"):
            st.session_state.vista = "volatilidad"

        if col2.button("👤 Responsables"):
            st.session_state.vista = "responsables"

        if col3.button("🔎 Causas"):
            st.session_state.vista = "causas"

        if col4.button("📄 Reporte Ejecutivo"):
            st.session_state.vista = "reporte"

    # =========================
    # 🚦 VOLATILIDAD
    # =========================
    elif st.session_state.vista == "volatilidad":

        st.title("🚦 Estabilidad del Negocio")

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        media = df_m["Ventas"].mean()
        vol = df_m["Ventas"].std()
        ratio = vol / media if media != 0 else 0

        if ratio > 0.30:
            st.markdown("🔴 **Alta inestabilidad**")
        elif ratio > 0.15:
            st.markdown("🟡 **Variabilidad moderada**")
        else:
            st.markdown("🟢 **Ventas estables**")

        st.line_chart(df_m.set_index("Periodo")["Ventas"])

    # =========================
    # 👤 RESPONSABLES
    # =========================
    elif st.session_state.vista == "responsables":

        st.title("👤 Responsables")

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        df_nom = df.groupby(["Periodo", "Nombre"])["Ventas"].sum().reset_index()

        impacto = []
        for n in df_nom["Nombre"].unique():
            df_n = df_nom[df_nom["Nombre"] == n]
            if len(df_n) > 1:
                impacto.append((n, df_n["Ventas"].std()))

        df_imp = pd.DataFrame(impacto, columns=["Nombre", "Volatilidad"])
        total = df_imp["Volatilidad"].sum()
        df_imp["Impacto %"] = (df_imp["Volatilidad"] / total) * 100
        df_imp = df_imp.sort_values("Impacto %", ascending=False).head(10)

        for _, row in df_imp.iterrows():
            st.write(f"{row['Nombre']} → {row['Impacto %']:.1f}%")

        fig = px.line(df_nom, x="Periodo", y="Ventas", color="Nombre")
        st.plotly_chart(fig, use_container_width=True)

    # =========================
    # 🔎 CAUSAS
    # =========================
    elif st.session_state.vista == "causas":

        st.title("🔎 Causas de la Volatilidad")

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        df_reg = df.groupby(["Periodo", "Region"])["Ventas"].sum().reset_index()

        impacto = []
        for r in df_reg["Region"].unique():
            df_r = df_reg[df_reg["Region"] == r]
            if len(df_r) > 1:
                impacto.append((r, df_r["Ventas"].std()))

        df_imp = pd.DataFrame(impacto, columns=["Region", "Volatilidad"])
        total = df_imp["Volatilidad"].sum()
        df_imp["Impacto %"] = (df_imp["Volatilidad"] / total) * 100
        df_imp = df_imp.sort_values("Impacto %", ascending=False)

        for _, row in df_imp.iterrows():
            st.write(f"{row['Region']} → {row['Impacto %']:.1f}%")

        fig = px.line(df_reg, x="Periodo", y="Ventas", color="Region")
        st.plotly_chart(fig, use_container_width=True)

    # =========================
    # 📄 REPORTE EJECUTIVO
    # =========================
    elif st.session_state.vista == "reporte":

        st.title("📄 Reporte Ejecutivo")

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        ventas = df["Ventas"].sum()
        ganancia = df["Ganancia"].sum()
        margen = (ganancia / ventas * 100) if ventas != 0 else 0

        crecimiento = df_m["Ventas"].pct_change().mean() * 100

        st.markdown("## 🧾 Resumen")

        st.write(f"- Ventas totales: ${ventas:,.0f}")
        st.write(f"- Ganancia total: ${ganancia:,.0f}")
        st.write(f"- Margen: {margen:.1f}%")
        st.write(f"- Crecimiento promedio: {crecimiento:.1f}%")

        if crecimiento > 0:
            st.success("El negocio muestra una tendencia positiva.")
        else:
            st.error("El negocio presenta una tendencia negativa.")

        max_mes = df_m.loc[df_m["Ventas"].idxmax()]
        min_mes = df_m.loc[df_m["Ventas"].idxmin()]

        st.markdown("## 📊 Hallazgos")

        st.write(f"- Mejor periodo: {max_mes['Periodo']} (${max_mes['Ventas']:,.0f})")
        st.write(f"- Peor periodo: {min_mes['Periodo']} (${min_mes['Ventas']:,.0f})")

        st.markdown("## 🎯 Conclusión")

        st.info("Se recomienda enfocar esfuerzos en las regiones y responsables con mayor variabilidad.")

else:
    st.info("Sube archivo Excel")
