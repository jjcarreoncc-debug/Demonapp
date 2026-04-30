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
        # PROYECCIÓN MULTIPERIODO
        # -------------------------
        st.subheader("📈 Proyección")

        if len(df_m) > 2:

            tendencia = df_m["Ventas"].diff().mean()

            ultimo_periodo = pd.Period(df_m["Periodo"].iloc[-1], freq="M")
            ultimo_valor = df_m["Ventas"].iloc[-1]

            proyecciones = []
            periodo_actual = ultimo_periodo
            valor_actual = ultimo_valor

            while periodo_actual.month < 12:
                periodo_actual += 1
                valor_actual += tendencia

                proyecciones.append({
                    "Periodo": periodo_actual.strftime("%Y-%m"),
                    "Ventas": valor_actual,
                    "Tipo": "Proyección"
                })

            df_real = df_m.copy()
            df_real["Tipo"] = "Real"

            df_proj = pd.DataFrame(proyecciones)

            df_final = pd.concat([
                df_real[["Periodo", "Ventas", "Tipo"]],
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

            st.caption("Proyección hasta cierre de año basada en tendencia histórica.")

        # -------------------------
        # GAUGES / SEMÁFOROS
        # -------------------------
        st.subheader("🎯 Palancas de Crecimiento")

        def calcular_crecimiento(df, columna):

            df_temp = df.groupby(["Periodo", columna])["Ventas"].sum().reset_index()
            ultimos = df_temp.sort_values("Periodo").groupby(columna).tail(2)

            crecimiento_dict = {}

            for key, grupo in ultimos.groupby(columna):
                if len(grupo) == 2:
                    v1 = grupo.iloc[0]["Ventas"]
                    v2 = grupo.iloc[1]["Ventas"]

                    if v1 != 0:
                        crecimiento = (v2 - v1) / v1
                        crecimiento_dict[key] = crecimiento

            return crecimiento_dict

        # PAIS
        if "Pais" in df.columns:
            st.markdown("### 🌎 País")
            for k, v in calcular_crecimiento(df, "Pais").items():
                if v > 0.05:
                    st.success(f"{k}: 🟢 {v*100:.1f}% crecimiento")
                elif v > -0.05:
                    st.warning(f"{k}: 🟡 {v*100:.1f}% estable")
                else:
                    st.error(f"{k}: 🔴 {v*100:.1f}% caída")

        # REGION
        if "Region" in df.columns:
            st.markdown("### 🗺 Región")
            for k, v in calcular_crecimiento(df, "Region").items():
                if v > 0.05:
                    st.success(f"{k}: 🟢 {v*100:.1f}% crecimiento")
                elif v > -0.05:
                    st.warning(f"{k}: 🟡 {v*100:.1f}% estable")
                else:
                    st.error(f"{k}: 🔴 {v*100:.1f}% caída")

        # CANAL
        if "Canal" in df.columns:
            st.markdown("### 📡 Canal")
            for k, v in calcular_crecimiento(df, "Canal").items():
                if v > 0.05:
                    st.success(f"{k}: 🟢 {v*100:.1f}% crecimiento")
                elif v > -0.05:
                    st.warning(f"{k}: 🟡 {v*100:.1f}% estable")
                else:
                    st.error(f"{k}: 🔴 {v*100:.1f}% caída")

else:
    st.info("📂 Sube archivo")
