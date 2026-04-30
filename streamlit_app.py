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
    # CONVERSIÓN A NUMÉRICO (ANTI-ERROR)
    # -------------------------

cols_numericas = ["Ventas_Cantidad", "Precio_Venta", "Costos_Venta", "Ventas", "Costos"]

for col in cols_numericas:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")    
    
    # -------------------------
    # LIMPIEZA
    # -------------------------
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df = df.dropna(subset=["Fecha"])

    # -------------------------
    # CALCULOS FLEXIBLES
    # -------------------------
    # Ventas
    if "Ventas_Cantidad" in df.columns and "Precio_Venta" in df.columns:
        df["Ventas"] = df["Ventas_Cantidad"] * df["Precio_Venta"]
    else:
        df["Ventas"] = df.get("Ventas", 0)

    # Costos
    if "Costos_Venta" in df.columns and "Ventas_Cantidad" in df.columns:
        df["Costos"] = df["Ventas_Cantidad"] * df["Costos_Venta"]
    else:
        df["Costos"] = df.get("Costos", 0)

    # Ganancia
    df["Ganancia"] = df["Ventas"] - df["Costos"]

    # Periodo
    df["Periodo"] = df["Fecha"].dt.to_period("M").astype(str)

    # -------------------------
    # FILTROS
    # -------------------------
    st.sidebar.header("🎯 Filtros")

    rango = st.sidebar.date_input(
        "Fecha",
        [df["Fecha"].min(), df["Fecha"].max()]
    )

    if len(rango) == 2:
        df = df[(df["Fecha"] >= pd.to_datetime(rango[0])) &
                (df["Fecha"] <= pd.to_datetime(rango[1]))]

    if "Pais" in df.columns:
        pais = st.sidebar.multiselect("País", df["Pais"].unique(), df["Pais"].unique())
        df = df[df["Pais"].isin(pais)]

    if "Region" in df.columns:
        region = st.sidebar.multiselect("Región", df["Region"].unique(), df["Region"].unique())
        df = df[df["Region"].isin(region)]

    if "Vendedor_Ruta" in df.columns:
        ruta = st.sidebar.multiselect("Ruta", df["Vendedor_Ruta"].unique(), df["Vendedor_Ruta"].unique())
        df = df[df["Vendedor_Ruta"].isin(ruta)]

    if "Canal" in df.columns:
        canal = st.sidebar.multiselect("Canal", df["Canal"].unique(), df["Canal"].unique())
        df = df[df["Canal"].isin(canal)]

    if df.empty:
        st.warning("⚠️ No hay datos")
        st.stop()

    # -------------------------
    # CALCULOS GENERALES
    # -------------------------
    df_m = df.groupby("Periodo")[["Ventas", "Ganancia"]].sum().reset_index()

    ventas = df["Ventas"].sum()
    ganancia = df["Ganancia"].sum()
    margen = (ganancia / ventas * 100) if ventas != 0 else 0

    media = df_m["Ventas"].mean()
    volatilidad = df_m["Ventas"].std()
    ratio = volatilidad / media if media != 0 else 0

    # =========================
    # PRINCIPAL
    # =========================
    if st.session_state.vista == "principal":

        st.title("📊 Dashboard Ejecutivo")

        c1, c2, c3 = st.columns(3)
        c1.metric("Ventas", f"${ventas:,.0f}")
        c2.metric("Ganancia", f"${ganancia:,.0f}")
        c3.metric("Margen", f"{margen:.1f}%")

        fig = px.line(df_m, x="Periodo", y=["Ventas", "Ganancia"], markers=True)
        st.plotly_chart(fig, use_container_width=True)

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

    # =========================
    # RESPONSABLES
    # =========================
    elif st.session_state.vista == "responsables":

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        st.title("👤 Responsables")

        col_resp = None
        if "Vendedor_Ruta" in df.columns:
            col_resp = "Vendedor_Ruta"
        elif "Nombre" in df.columns:
            col_resp = "Nombre"

        if col_resp:
            df_resp = df.groupby(col_resp)["Ventas"].sum().sort_values(ascending=False)

            st.subheader("🏆 Ranking")
            st.dataframe(df_resp)

            df_var = df.groupby(["Periodo", col_resp])["Ventas"].sum().reset_index()

            fig = px.line(df_var, x="Periodo", y="Ventas", color=col_resp)
            st.plotly_chart(fig, use_container_width=True)

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

        if "Canal" in df.columns:
            df_canal = df.groupby("Canal")["Ventas"].sum().sort_values(ascending=False)
            st.subheader("Impacto por canal")
            st.bar_chart(df_canal)

        if "Vendedor_Ruta" in df.columns:
            df_ruta = df.groupby("Vendedor_Ruta")["Ventas"].sum().sort_values(ascending=False)
            st.subheader("Impacto por ruta")
            st.bar_chart(df_ruta)

        if ratio > 0.30:
            st.error("Posible causa: alta variabilidad")
        elif ratio > 0.15:
            st.warning("Posible causa: diferencias por canal/región")
        else:
            st.success("Sistema estable")

else:
    st.info("📂 Sube archivo")
