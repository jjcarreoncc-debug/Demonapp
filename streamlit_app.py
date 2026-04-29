# === DASHBOARD PRO CON DISEÑO ===

import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(page_title="Dashboard Ejecutivo PRO", layout="wide")

# -------------------------
# ESTILO GLOBAL
# -------------------------
st.markdown("""
<style>
body {
    background-color: #f7f9fb;
}
.block-container {
    padding-top: 1.5rem;
}
div[data-testid="stMetric"] {
    background-color: white;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
}
h1, h2, h3 {
    font-weight: 600;
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
    # PRINCIPAL
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

        # Gráfica limpia
        fig = px.line(df_m, x="Periodo", y=["Ventas", "Ganancia"], markers=True)
        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            hovermode="x unified"
        )
        fig.update_traces(line=dict(width=3))
        st.plotly_chart(fig, use_container_width=True)

        # Navegación
        st.markdown("## 📊 Explorar análisis")

        col1, col2, col3 = st.columns(3)

        if col1.button("🚦 Volatilidad del negocio"):
            st.session_state.vista = "volatilidad"

        if col2.button("👤 Responsables clave"):
            st.session_state.vista = "responsables"

        if col3.button("🔎 Causas de variación"):
            st.session_state.vista = "causas"

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

        st.markdown("### Estado del negocio")

        if ratio > 0.30:
            st.markdown("🔴 **Alta inestabilidad**")
        elif ratio > 0.15:
            st.markdown("🟡 **Variabilidad moderada**")
        else:
            st.markdown("🟢 **Ventas estables**")

        fig = px.line(df_m, x="Periodo", y="Ventas", markers=True)
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    # =========================
    # RESPONSABLES
    # =========================
    elif st.session_state.vista == "responsables":

        st.title("👤 Responsables")

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        if "Nombre" in df.columns:

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
                if row["Impacto %"] > 30:
                    st.markdown(f"🔴 **{row['Nombre']} → {row['Impacto %']:.1f}%**")
                elif row["Impacto %"] > 15:
                    st.markdown(f"🟡 **{row['Nombre']} → {row['Impacto %']:.1f}%**")
                else:
                    st.markdown(f"🟢 **{row['Nombre']} → {row['Impacto %']:.1f}%**")

            fig = px.line(df_nom, x="Periodo", y="Ventas", color="Nombre")
            fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig, use_container_width=True)

    # =========================
    # CAUSAS
    # =========================
    elif st.session_state.vista == "causas":

        st.title("🔎 Causas de la Volatilidad")

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        if "Region" in df.columns:

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
                if row["Impacto %"] > 40:
                    st.markdown(f"🔴 **{row['Region']} → {row['Impacto %']:.1f}%**")
                elif row["Impacto %"] > 20:
                    st.markdown(f"🟡 **{row['Region']} → {row['Impacto %']:.1f}%**")
                else:
                    st.markdown(f"🟢 **{row['Region']} → {row['Impacto %']:.1f}%**")

            fig = px.line(df_reg, x="Periodo", y="Ventas", color="Region")
            fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Sube archivo Excel")
