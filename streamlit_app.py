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
    # CALCULOS
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

    rango = st.sidebar.date_input("Fecha", [df["Fecha"].min(), df["Fecha"].max()])

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

        col1, col2, col3, col4, col5, col6 = st.columns(6)

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

        if col6.button("📌 Recomendaciones"):
            st.session_state.vista = "recomendaciones"

    # =========================
    # RESUMEN EJECUTIVO
    # =========================
    elif st.session_state.vista == "resumen":

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        st.title("🧠 Resumen Ejecutivo")

        score = 100
        if margen < 10:
            score -= 20
        if ratio > 0.30:
            score -= 20

        if score >= 80:
            st.success(f"🟢 Salud Alta ({score})")
        elif score >= 50:
            st.warning(f"🟡 Salud Media ({score})")
        else:
            st.error(f"🔴 Salud Crítica ({score})")

        st.subheader("📈 Proyección")

        if len(df_m) > 2:
            tendencia = df_m["Ventas"].diff().mean()
            ultimo = df_m["Ventas"].iloc[-1]

            df_m["Proyección"] = df_m["Ventas"]
            for i in range(len(df_m)):
                df_m.loc[i, "Proyección"] = ultimo + (i * tendencia)

            fig = px.line(df_m, x="Periodo", y=["Ventas", "Proyección"], markers=True)
            st.plotly_chart(fig, use_container_width=True)

    # =========================
    # RECOMENDACIONES PPT
    # =========================
    elif st.session_state.vista == "recomendaciones":

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        st.title("📌 Recomendaciones Estratégicas")

        recomendaciones = []

        def generar(df, col):
            df_t = df.groupby(["Periodo", col])["Ventas"].sum().reset_index()
            df_t = df_t.sort_values("Periodo")

            for k, g in df_t.groupby(col):
                if len(g) >= 2 and g.iloc[-2]["Ventas"] != 0:
                    var = (g.iloc[-1]["Ventas"] - g.iloc[-2]["Ventas"]) / g.iloc[-2]["Ventas"]

                    if var < -0.10:
                        recomendaciones.append(("rojo", f"Recuperar {col}: {k}", var))
                    elif var > 0.10:
                        recomendaciones.append(("verde", f"Escalar {col}: {k}", var))

        for dim in ["Pais", "Region", "Canal"]:
            if dim in df.columns:
                generar(df, dim)

        if "Producto" in df.columns:
            generar(df, "Producto")
        elif "Nombre_Producto" in df.columns:
            generar(df, "Nombre_Producto")

        for tipo, texto, var in recomendaciones:

            if tipo == "verde":
                st.success(f"""
                ### 🟢 {texto}
                #### Crecimiento: {var*100:.1f}%

                👉 Potenciar este segmento
                """)
            else:
                st.error(f"""
                ### 🔴 {texto}
                #### Caída: {var*100:.1f}%

                👉 Intervenir inmediatamente
                """)

            st.markdown("---")

    # =========================
    # DETALLE VACÍO
    # =========================
    elif st.session_state.vista == "detalle":

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        st.title("🔎 Análisis Detallado")
        st.info("Módulo en construcción")

else:
    st.info("📂 Sube archivo")
