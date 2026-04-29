# === VERSION COMPLETA + MODO DIRECTOR (SIN ROMPER BASE) ===

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
# CARGA
# -------------------------
archivo = st.file_uploader("📂 Sube tu archivo Excel", type=["xlsx"])

if archivo:

    df = pd.read_excel(archivo)
    df.columns = df.columns.str.strip()

    # -------------------------
    # VALIDACIONES
    # -------------------------
    columnas_necesarias = ["Fecha", "Ventas", "Costos"]
    faltantes = [col for col in columnas_necesarias if col not in df.columns]

    if faltantes:
        st.error(f"Faltan columnas obligatorias: {faltantes}")
        st.stop()

    df["Ventas"] = pd.to_numeric(df["Ventas"], errors="coerce")
    df["Costos"] = pd.to_numeric(df["Costos"], errors="coerce")
    df = df.dropna(subset=["Ventas", "Costos"])

    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")

    if df["Fecha"].isna().all():
        st.error("Todas las fechas son inválidas")
        st.stop()

    df = df.dropna(subset=["Fecha"])

    # -------------------------
    # CALCULOS
    # -------------------------
    df["Ganancia"] = df["Ventas"] - df["Costos"]
    df["Periodo"] = df["Fecha"].dt.to_period("M").astype(str)

    # -------------------------
    # FILTROS
    # -------------------------
    st.sidebar.header("🎯 Filtros")

    rango = st.sidebar.date_input("Fecha",
        [df["Fecha"].min(), df["Fecha"].max()]
    )

    if len(rango) == 2:
        df = df[(df["Fecha"] >= pd.to_datetime(rango[0])) &
                (df["Fecha"] <= pd.to_datetime(rango[1]))]

    if "Pais" in df.columns:
        pais = st.sidebar.multiselect("País", df["Pais"].unique(), df["Pais"].unique())
        if pais:
            df = df[df["Pais"].isin(pais)]

    if "Region" in df.columns:
        region = st.sidebar.multiselect("Región", df["Region"].unique(), df["Region"].unique())
        if region:
            df = df[df["Region"].isin(region)]

    if "Nombre" in df.columns:
        nombre = st.sidebar.multiselect("Responsable", df["Nombre"].unique(), df["Nombre"].unique())
        if nombre:
            df = df[df["Nombre"].isin(nombre)]

    if df.empty:
        st.warning("⚠️ No hay datos")
        st.stop()

    # -------------------------
    # AGRUPACION
    # -------------------------
    df_m = df.groupby("Periodo")[["Ventas", "Ganancia"]].sum().reset_index()
    df_m = df_m.sort_values("Periodo")

    ventas = df["Ventas"].sum()
    ganancia = df["Ganancia"].sum()

    if ventas == 0:
        margen = 0
    else:
        margen = ganancia / ventas * 100

    media = df_m["Ventas"].mean()
    volatilidad = df_m["Ventas"].std()

    if len(df_m) < 3 or media == 0:
        ratio = 0
    else:
        ratio = volatilidad / media

    # Tendencia
    df_m["Ventas_prev"] = df_m["Ventas"].shift(1)
    df_m["Cambio_%"] = ((df_m["Ventas"] - df_m["Ventas_prev"]) / df_m["Ventas_prev"]) * 100
    ultimo_cambio = df_m["Cambio_%"].iloc[-1] if len(df_m) > 1 else 0

    # =========================
    # PRINCIPAL
    # =========================
    if st.session_state.vista == "principal":

        st.title("📊 Dashboard Ejecutivo")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Ventas", f"${ventas:,.0f}")
        c2.metric("Ganancia", f"${ganancia:,.0f}")
        c3.metric("Margen", f"{margen:.1f}%")
        c4.metric("Tendencia", f"{ultimo_cambio:.1f}%", delta=f"{ultimo_cambio:.1f}%")

        # -------------------------
        # RESUMEN EJECUTIVO
        # -------------------------
        st.markdown("## 🧭 Resumen Ejecutivo")

        if ventas == 0:
            st.warning("No hay ventas registradas en el periodo seleccionado.")
        elif ganancia < 0:
            st.error("El negocio está generando pérdidas.")
        elif margen < 10:
            st.warning("Rentabilidad baja. Se requiere acción.")
        elif ratio > 0.30:
            st.warning("Ingresos inestables. Alta volatilidad.")
        else:
            st.success("El negocio muestra un comportamiento saludable.")

        # -------------------------
        # ALERTAS
        # -------------------------
        st.markdown("### 🚨 Alertas clave")

        if ganancia < 0:
            st.error("Pérdidas detectadas")

        if margen < 10:
            st.warning("Margen bajo")

        if ratio > 0.30:
            st.warning("Alta volatilidad")

        # -------------------------
        # INSIGHTS
        # -------------------------
        if "Nombre" in df.columns:
            df_resp = df.groupby("Nombre")["Ventas"].sum()
            mejor = df_resp.idxmax()
            peor = df_resp.idxmin()

            st.markdown("### 👥 Responsables")
            st.success(f"Mejor desempeño: {mejor}")
            st.error(f"Mayor oportunidad: {peor}")

        if "Region" in df.columns:
            df_reg = df.groupby("Region")["Ventas"].sum()
            st.markdown("### 🌎 Regiones")
            st.info(f"Mayor aporte: {df_reg.idxmax()}")
            st.warning(f"Menor desempeño: {df_reg.idxmin()}")

            participacion = (df_reg / ventas * 100).sort_values(ascending=False)
            st.bar_chart(participacion)

        # -------------------------
        # GRAFICO
        # -------------------------
        fig = px.line(df_m, x="Periodo", y=["Ventas", "Ganancia"], markers=True)
        st.plotly_chart(fig, use_container_width=True)

        # -------------------------
        # NAVEGACION
        # -------------------------
        col1, col2, col3 = st.columns(3)

        if col1.button("🚦 Volatilidad"):
            st.session_state.vista = "volatilidad"

        if col2.button("👤 Responsables"):
            st.session_state.vista = "responsables"

        if col3.button("🧠 Causas"):
            st.session_state.vista = "causas"

    # =========================
    # VOLATILIDAD
    # =========================
    elif st.session_state.vista == "volatilidad":

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        st.title("🚦 Volatilidad")

        if ratio > 0.30:
            st.error("🔴 Alta volatilidad")
        elif ratio > 0.15:
            st.warning("🟡 Volatilidad media")
        else:
            st.success("🟢 Estabilidad")

        st.line_chart(df_m.set_index("Periodo")["Ventas"])

        st.markdown(f"""
        **Detalle técnico**
        - Media: {media:,.0f}
        - Desviación: {volatilidad:,.0f}
        - Ratio: {ratio:.2f}
        """)

    # =========================
    # RESPONSABLES
    # =========================
    elif st.session_state.vista == "responsables":

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        st.title("👤 Responsables")

        if "Nombre" in df.columns:

            df_resp = df.groupby("Nombre")["Ventas"].sum().sort_values(ascending=False)
            st.subheader("🏆 Ranking")
            st.dataframe(df_resp)

            df_var = df.groupby(["Periodo","Nombre"])["Ventas"].sum().reset_index()
            fig = px.line(df_var, x="Periodo", y="Ventas", color="Nombre")
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("No existe columna Nombre")

    # =========================
    # CAUSAS
    # =========================
    elif st.session_state.vista == "causas":

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        st.title("🧠 Análisis de Causas")

        if "Region" in df.columns:
            df_reg = df.groupby("Region")["Ventas"].sum().sort_values(ascending=False)
            st.subheader("Impacto por región")
            st.bar_chart(df_reg)

        if "Nombre" in df.columns:
            df_nom = df.groupby("Nombre")["Ventas"].sum().sort_values()
            st.subheader("Responsables con menor desempeño")
            st.dataframe(df_nom.head(5))

        if ratio > 0.30:
            st.error("Posible causa: alta dependencia")
        elif ratio > 0.15:
            st.warning("Posible causa: variaciones regionales")
        else:
            st.success("Sistema estable")
