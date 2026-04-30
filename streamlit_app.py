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
    # LIMPIEZA
    # -------------------------
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df = df.dropna(subset=["Fecha"])

    # -------------------------
    # CONVERSIÓN NUMÉRICA
    # -------------------------
    cols_numericas = ["Ventas_Cantidad", "Precio_Venta", "Costos_Venta", "Ventas", "Costos", "Objetivo"]

    for col in cols_numericas:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", "")
                .str.replace("$", "")
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # -------------------------
    # CALCULOS FLEXIBLES
    # -------------------------
    if "Ventas_Cantidad" in df.columns and "Precio_Venta" in df.columns:
        df["Ventas"] = df["Ventas_Cantidad"] * df["Precio_Venta"]
    else:
        df["Ventas"] = df.get("Ventas", 0)

    if "Costos_Venta" in df.columns and "Ventas_Cantidad" in df.columns:
        df["Costos"] = df["Ventas_Cantidad"] * df["Costos_Venta"]
    else:
        df["Costos"] = df.get("Costos", 0)

    df["Ganancia"] = df["Ventas"] - df["Costos"]
    df["Periodo"] = df["Fecha"].dt.to_period("M").astype(str)

    # -------------------------
    # INDICADORES
    # -------------------------
    if "Objetivo" in df.columns:
        df["Cumplimiento"] = df["Ventas"] / df["Objetivo"]
    else:
        df["Cumplimiento"] = None

    if "Ventas_Cantidad" in df.columns:
        total_unidades = df["Ventas_Cantidad"].sum()
        ticket = df["Ventas"].sum() / total_unidades if total_unidades != 0 else 0
    else:
        ticket = 0

    # -------------------------
    # FILTROS BASE
    # -------------------------
    st.sidebar.header("🎯 Filtros Base")

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

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Ventas", f"${ventas:,.0f}")
        c2.metric("Ganancia", f"${ganancia:,.0f}")
        c3.metric("Margen", f"{margen:.1f}%")

        if df["Cumplimiento"].notna().any():
            cumplimiento_total = df["Cumplimiento"].mean() * 100
            c4.metric("Cumplimiento", f"{cumplimiento_total:.1f}%")

        st.metric("Ticket Promedio", f"${ticket:,.0f}")

        fig = px.line(df_m, x="Periodo", y=["Ventas", "Ganancia"], markers=True)
        st.plotly_chart(fig, use_container_width=True)

        col1, col2, col3, col4, col5 = st.columns(5)

        if col1.button("🚦 Volatilidad"):
            st.session_state.vista = "volatilidad"

        if col2.button("👤 Responsables"):
            st.session_state.vista = "responsables"

        if col3.button("🧠 Causas"):
            st.session_state.vista = "causas"

        if col4.button("🔎 Análisis Detallado"):
            st.session_state.vista = "detalle"

        if col5.button("🧠 Resumen Ejecutivo"):
            st.session_state.vista = "resumen"

    # =========================
    # RESUMEN EJECUTIVO
    # =========================
    elif st.session_state.vista == "resumen":

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        st.title("🧠 Resumen Ejecutivo")

        # SCORE
        score = 100

        if margen < 10:
            score -= 20

        if ratio > 0.30:
            score -= 20

        if df["Cumplimiento"].notna().any():
            cumplimiento_total = df["Cumplimiento"].mean()
            if cumplimiento_total < 0.8:
                score -= 30

        st.subheader("Estado del negocio")

        if score >= 80:
            st.success(f"🟢 Salud Alta ({score})")
        elif score >= 50:
            st.warning(f"🟡 Salud Media ({score})")
        else:
            st.error(f"🔴 Salud Crítica ({score})")

        # -------------------------
        # PROYECCIÓN MEJORADA
        # -------------------------
        st.subheader("📈 Proyección")

        if len(df_m) > 2:

            tendencia = df_m["Ventas"].diff().mean()
            prediccion = df_m["Ventas"].iloc[-1] + tendencia

            st.metric("Próximo periodo", f"${prediccion:,.0f}")

            df_pred = df_m.copy()

            ultimo_periodo = pd.Period(df_pred["Periodo"].iloc[-1], freq="M")
            siguiente_periodo = (ultimo_periodo + 1).strftime("%Y-%m")

            df_pred["Tipo"] = "Real"

            df_proj = pd.DataFrame({
                "Periodo": [df_pred["Periodo"].iloc[-1], siguiente_periodo],
                "Ventas": [df_pred["Ventas"].iloc[-1], prediccion],
                "Tipo": ["Proyección", "Proyección"]
            })

            df_final = pd.concat([
                df_pred[["Periodo", "Ventas", "Tipo"]],
                df_proj
            ], ignore_index=True)

            fig = px.line(
                df_final,
                x="Periodo",
                y="Ventas",
                color="Tipo",
                markers=True
            )

            st.plotly_chart(fig, use_container_width=True)

            st.caption("Comparación entre ventas reales y proyección.")

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

        col_resp = "Vendedor_Ruta" if "Vendedor_Ruta" in df.columns else "Nombre"

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
            st.bar_chart(df.groupby("Region")["Ventas"].sum())

        if ratio > 0.30:
            st.error("Alta variabilidad")
        elif ratio > 0.15:
            st.warning("Variación moderada")
        else:
            st.success("Estable")

else:
    st.info("📂 Sube archivo")
