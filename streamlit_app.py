import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(page_title="Dashboard Ejecutivo PRO", layout="wide")

# -------------------------
# NAVEGACIÓN
# -------------------------
if "vista" not in st.session_state:
    st.session_state.vista = "principal"

# -------------------------
# CACHE
# -------------------------
@st.cache_data
def cargar_datos(archivo):
    df = pd.read_excel(archivo)
    df.columns = df.columns.str.strip()
    return df

# -------------------------
# PREPARAR
# -------------------------
def preparar(df):
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df = df.dropna(subset=["Fecha"])
    df["Ganancia"] = df["Ventas"] - df["Costos"]
    df["Periodo"] = df["Fecha"].dt.to_period("M").astype(str)
    return df

# -------------------------
# UI
# -------------------------
st.title("📊 Dashboard Ejecutivo PRO")
archivo = st.file_uploader("Sube tu Excel", type=["xlsx"])

if archivo:

    df = cargar_datos(archivo)
    df = preparar(df)

    # -------------------------
    # FILTROS INTELIGENTES
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

    # -------------------------
    # AGRUPACIÓN
    # -------------------------
    df_m = df.groupby("Periodo")[["Ventas", "Ganancia"]].sum().reset_index()

    # =========================
    # 🏠 PRINCIPAL
    # =========================
    if st.session_state.vista == "principal":

        st.subheader("Resumen Ejecutivo")

        ventas = df["Ventas"].sum()
        ganancia = df["Ganancia"].sum()
        margen = (ganancia / ventas * 100) if ventas != 0 else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("Ventas", f"${ventas:,.0f}")
        c2.metric("Ganancia", f"${ganancia:,.0f}")
        c3.metric("Margen", f"{margen:.1f}%")

        # Tendencia
        fig = px.line(df_m, x="Periodo", y=["Ventas", "Ganancia"], markers=True)
        st.plotly_chart(fig, use_container_width=True)

        # Navegación
        st.markdown("## 📊 Análisis")

        col1, col2, col3 = st.columns(3)

        if col1.button("🚦 Volatilidad"):
            st.session_state.vista = "volatilidad"

        if col2.button("👤 Responsables"):
            st.session_state.vista = "responsables"

        if col3.button("🔎 Causas"):
            st.session_state.vista = "causas"

    # =========================
    # 🚦 VOLATILIDAD
    # =========================
    elif st.session_state.vista == "volatilidad":

        st.title("🚦 Volatilidad del Negocio")

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        media = df_m["Ventas"].mean()
        vol = df_m["Ventas"].std()
        ratio = vol / media if media != 0 else 0

        # SEMÁFORO
        if ratio > 0.30:
            st.error(f"🔴 Alta inestabilidad ({ratio:.2f})")
        elif ratio > 0.15:
            st.warning(f"🟡 Variabilidad moderada ({ratio:.2f})")
        else:
            st.success(f"🟢 Estable ({ratio:.2f})")

        # GRÁFICA
        fig = px.line(df_m, x="Periodo", y="Ventas", markers=True)
        st.plotly_chart(fig, use_container_width=True)

    # =========================
    # 👤 RESPONSABLES
    # =========================
    elif st.session_state.vista == "responsables":

        st.title("👤 Responsables de la Variabilidad")

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        if "Nombre" in df.columns:

            df_nom = df.groupby(["Periodo", "Nombre"])["Ventas"].sum().reset_index()

            impacto = []

            for n in df_nom["Nombre"].unique():
                df_n = df_nom[df_nom["Nombre"] == n]

                if len(df_n) > 1:
                    vol = df_n["Ventas"].std()
                    impacto.append((n, vol))

            df_imp = pd.DataFrame(impacto, columns=["Nombre", "Volatilidad"])

            total = df_imp["Volatilidad"].sum()
            df_imp["Impacto %"] = (df_imp["Volatilidad"] / total) * 100
            df_imp = df_imp.sort_values("Impacto %", ascending=False).head(10)

            # SEMÁFORO + TEXTO
            for _, row in df_imp.iterrows():

                if row["Impacto %"] > 30:
                    st.error(f"{row['Nombre']} → {row['Impacto %']:.1f}%")
                elif row["Impacto %"] > 15:
                    st.warning(f"{row['Nombre']} → {row['Impacto %']:.1f}%")
                else:
                    st.success(f"{row['Nombre']} → {row['Impacto %']:.1f}%")

            # GRÁFICA
            fig = px.line(df_nom, x="Periodo", y="Ventas", color="Nombre")
            st.plotly_chart(fig, use_container_width=True)

    # =========================
    # 🔎 CAUSAS
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
                    vol = df_r["Ventas"].std()
                    impacto.append((r, vol))

            df_imp = pd.DataFrame(impacto, columns=["Region", "Volatilidad"])

            total = df_imp["Volatilidad"].sum()
            df_imp["Impacto %"] = (df_imp["Volatilidad"] / total) * 100
            df_imp = df_imp.sort_values("Impacto %", ascending=False)

            # SEMÁFORO
            for _, row in df_imp.iterrows():

                if row["Impacto %"] > 40:
                    st.error(f"{row['Region']} → {row['Impacto %']:.1f}%")
                elif row["Impacto %"] > 20:
                    st.warning(f"{row['Region']} → {row['Impacto %']:.1f}%")
                else:
                    st.success(f"{row['Region']} → {row['Impacto %']:.1f}%")

            # GRÁFICA
            fig = px.line(df_reg, x="Periodo", y="Ventas", color="Region")
            st.plotly_chart(fig, use_container_width=True)

