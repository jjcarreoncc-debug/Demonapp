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
# VALIDACIÓN
# -------------------------
def validar(df):
    for col in ["Fecha", "Ventas", "Costos"]:
        if col not in df.columns:
            st.error(f"Falta columna: {col}")
            st.stop()

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
    validar(df)
    df = preparar(df)

    # -------------------------
    # FILTROS INTELIGENTES
    # -------------------------
    st.sidebar.header("🔎 Filtros")

    df_filtrado = df.copy()

    # País
    if "Pais" in df.columns:
        paises = sorted(df["Pais"].dropna().unique())
        pais_sel = st.sidebar.multiselect("País", paises, default=paises)
        if pais_sel:
            df_filtrado = df_filtrado[df_filtrado["Pais"].isin(pais_sel)]

    # Región dependiente
    if "Region" in df.columns:
        regiones = sorted(df_filtrado["Region"].dropna().unique())
        reg_sel = st.sidebar.multiselect("Región", regiones, default=regiones)
        if reg_sel:
            df_filtrado = df_filtrado[df_filtrado["Region"].isin(reg_sel)]

    # Nombre dependiente
    if "Nombre" in df.columns:
        nombres = sorted(df_filtrado["Nombre"].dropna().unique())
        nom_sel = st.sidebar.multiselect("Nombre", nombres, default=nombres)
        if nom_sel:
            df_filtrado = df_filtrado[df_filtrado["Nombre"].isin(nom_sel)]

    df = df_filtrado

    if df.empty:
        st.warning("Sin datos")
        st.stop()

    # -------------------------
    # AGRUPACIÓN
    # -------------------------
    df_m = df.groupby("Periodo")[["Ventas", "Ganancia"]].sum().reset_index().sort_values("Periodo")

    # -------------------------
    # PANTALLA PRINCIPAL
    # -------------------------
    if st.session_state.vista == "principal":

        # KPIs
        ventas = df["Ventas"].sum()
        ganancia = df["Ganancia"].sum()
        margen = (ganancia / ventas * 100) if ventas != 0 else 0

        if len(df_m) > 1:
            var = ((df_m.iloc[-1]["Ventas"] - df_m.iloc[-2]["Ventas"]) /
                   df_m.iloc[-2]["Ventas"]) * 100
        else:
            var = 0

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Ventas", f"${ventas:,.0f}", f"{var:.1f}%")
        c2.metric("Ganancia", f"${ganancia:,.0f}")
        c3.metric("Margen", f"{margen:.1f}%")

        fig_g = go.Figure(go.Indicator(
            mode="gauge+number",
            value=margen,
            title={'text': "Margen %"},
            gauge={
                'axis': {'range': [0, 100]},
                'steps': [
                    {'range': [0, 30], 'color': "#e74c3c"},
                    {'range': [30, 60], 'color': "#f1c40f"},
                    {'range': [60, 100], 'color': "#2ecc71"}
                ]
            }
        ))
        c4.plotly_chart(fig_g, use_container_width=True)

        # Tendencia
        st.markdown("### 📈 Tendencia")
        fig_line = px.line(df_m, x="Periodo", y=["Ventas", "Ganancia"], markers=True)
        st.plotly_chart(fig_line, use_container_width=True)

        # Navegación
        st.markdown("## 📊 Análisis Avanzado")

        col1, col2, col3 = st.columns(3)

        if col1.button("🚦 Volatilidad"):
            st.session_state.vista = "volatilidad"

        if col2.button("👤 Responsables"):
            st.session_state.vista = "responsables"

        if col3.button("🔎 Causas"):
            st.session_state.vista = "causas"

    # -------------------------
    # PANTALLA VOLATILIDAD
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
            st.success("Ventas estables")

        st.line_chart(df_m.set_index("Periodo")["Ventas"])

    # -------------------------
    # PANTALLA RESPONSABLES
    # -------------------------
    elif st.session_state.vista == "responsables":

        st.title("👤 Responsables")

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        if "Nombre" in df.columns:
            df_nom = df.groupby("Nombre")["Ventas"].sum().sort_values(ascending=False).head(10)
            st.dataframe(df_nom)

    # -------------------------
    # PANTALLA CAUSAS
    # -------------------------
    elif st.session_state.vista == "causas":

        st.title("🔎 Causas")

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        if "Region" in df.columns:
            df_reg = df.groupby("Region")["Ventas"].sum().sort_values(ascending=False)
            st.dataframe(df_reg)

else:
    st.info("Sube archivo Excel")
