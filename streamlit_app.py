# === VERSION ESTABLE SIN EXPORTES (3 MODULOS) ===

import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(page_title="Dashboard Ejecutivo", layout="wide")

if "vista" not in st.session_state:
    st.session_state.vista = "principal"

# -------------------------
# APP
# -------------------------
archivo = st.file_uploader("Sube tu Excel", type=["xlsx"])

if archivo:

    df = pd.read_excel(archivo)
    df.columns = df.columns.str.strip()

    # -------------------------
    # LIMPIEZA
    # -------------------------
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df = df.dropna(subset=["Fecha"])

    df["Ganancia"] = df["Ventas"] - df["Costos"]
    df["Periodo"] = df["Fecha"].dt.to_period("M").astype(str)

    # -------------------------
    # FILTROS
    # -------------------------
    st.sidebar.header("Filtros")

    rango = st.sidebar.date_input(
        "Fecha",
        [df["Fecha"].min(), df["Fecha"].max()]
    )

    if len(rango) == 2:
        df = df[(df["Fecha"] >= pd.to_datetime(rango[0])) &
                (df["Fecha"] <= pd.to_datetime(rango[1]))]

    if "Pais" in df.columns:
        pais = st.sidebar.multiselect(
            "País",
            df["Pais"].unique(),
            df["Pais"].unique()
        )
        df = df[df["Pais"].isin(pais)]

    if "Region" in df.columns:
        reg = st.sidebar.multiselect(
            "Región",
            df["Region"].unique(),
            df["Region"].unique()
        )
        df = df[df["Region"].isin(reg)]

    if "Nombre" in df.columns:
        nom = st.sidebar.multiselect(
            "Nombre",
            df["Nombre"].unique(),
            df["Nombre"].unique()
        )
        df = df[df["Nombre"].isin(nom)]

    if df.empty:
        st.warning("Sin datos con esos filtros")
        st.stop()

    # -------------------------
    # CALCULOS
    # -------------------------
    df_m = df.groupby("Periodo")[["Ventas", "Ganancia"]].sum().reset_index()

    ventas = df["Ventas"].sum()
    ganancia = df["Ganancia"].sum()
    margen = (ganancia / ventas * 100) if ventas != 0 else 0

    media = df_m["Ventas"].mean()
    vol = df_m["Ventas"].std()
    ratio = vol / media if media != 0 else 0

    # =========================
    # PRINCIPAL
    # =========================
    if st.session_state.vista == "principal":

        st.title("📊 Dashboard Ejecutivo")

        c1, c2, c3 = st.columns(3)
        c1.metric("Ventas", f"${ventas:,.0f}")
        c2.metric("Ganancia", f"${ganancia:,.0f}")
        c3.metric("Margen", f"{margen:.1f}%")

        fig = px.line(
            df_m,
            x="Periodo",
            y=["Ventas", "Ganancia"],
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)

        col1, col2, col3 = st.columns(3)

        if col1.button("🚦 Volatilidad"):
            st.session_state.vista = "volatilidad"

        if col2.button("👤 Responsables"):
            st.session_state.vista = "responsables"

        if col3.button("🏠 Volver / Refresh"):
            st.session_state.vista = "principal"

    # =========================
    # VOLATILIDAD
    # =========================
    elif st.session_state.vista == "volatilidad":

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        st.subheader("Análisis de Volatilidad")

        if ratio > 0.30:
            st.error("🔴 Alta volatilidad (riesgo alto)")
        elif ratio > 0.15:
            st.warning("🟡 Volatilidad media")
        else:
            st.success("🟢 Ventas estables")

        st.line_chart(df_m.set_index("Periodo")["Ventas"])

    # =========================
    # RESPONSABLES
    # =========================
    elif st.session_state.vista == "responsables":

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        st.subheader("Desempeño por Responsable")

        if "Nombre" in df.columns:
            df_nom = df.groupby(["Periodo", "Nombre"])["Ventas"].sum().reset_index()

            fig = px.line(
                df_nom,
                x="Periodo",
                y="Ventas",
                color="Nombre"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No existe columna 'Nombre'")

else:
    st.info("📂 Sube un archivo Excel para comenzar")
