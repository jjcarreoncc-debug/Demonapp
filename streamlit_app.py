import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Ejecutivo", layout="wide")

if "vista" not in st.session_state:
    st.session_state.vista = "principal"

archivo = st.file_uploader("📂 Sube tu archivo Excel", type=["xlsx"])

if archivo:

    df = pd.read_excel(archivo)
    df.columns = df.columns.str.strip()

    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df = df.dropna(subset=["Fecha"])

    for col in ["Ventas_Cantidad", "Precio_Venta", "Costos_Venta"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["Ventas"] = df.get("Ventas", df["Ventas_Cantidad"] * df.get("Precio_Venta", 1))
    df["Costos"] = df.get("Costos", df["Ventas_Cantidad"] * df.get("Costos_Venta", 0))
    df["Ganancia"] = df["Ventas"] - df["Costos"]
    df["Periodo"] = df["Fecha"].dt.to_period("M").astype(str)

    # -------------------------
    # FILTROS
    # -------------------------
    st.sidebar.header("🎯 Filtros")

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
        st.stop()

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
    # VOLATILIDAD
    # =========================
    elif st.session_state.vista == "volatilidad":

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        st.title("🚦 Volatilidad")

        if ratio > 0.3:
            st.error(f"Alta volatilidad ({ratio:.2f})")
        elif ratio > 0.15:
            st.warning(f"Volatilidad media ({ratio:.2f})")
        else:
            st.success(f"Volatilidad baja ({ratio:.2f})")

        st.caption(f"Media: {media:,.0f} | Desviación: {volatilidad:,.0f}")

        df_m["Periodo_dt"] = pd.to_datetime(df_m["Periodo"])

        fig = px.line(df_m, x="Periodo_dt", y="Ventas", markers=True)
        st.plotly_chart(fig, use_container_width=True)

        fig2 = px.scatter(df_m, x="Periodo_dt", y="Ventas", size="Ventas")
        st.plotly_chart(fig2, use_container_width=True)

    # =========================
    # RESPONSABLES
    # =========================
    elif st.session_state.vista == "responsables":

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        st.title("👤 Responsables")

        if "Vendedor_Ruta" in df.columns:

            df_r = df.groupby("Vendedor_Ruta")["Ventas"].sum().reset_index()
            df_r = df_r.sort_values("Ventas", ascending=False)

            st.subheader("🏆 Ranking de ventas")
            st.dataframe(df_r)

            fig = px.bar(df_r, x="Vendedor_Ruta", y="Ventas")
            st.plotly_chart(fig, use_container_width=True)

            top = df_r.head(3)["Vendedor_Ruta"]
            df_top = df[df["Vendedor_Ruta"].isin(top)]
            df_t = df_top.groupby(["Periodo", "Vendedor_Ruta"])["Ventas"].sum().reset_index()

            fig2 = px.line(df_t, x="Periodo", y="Ventas", color="Vendedor_Ruta", markers=True)
            st.plotly_chart(fig2, use_container_width=True)

    # =========================
    # CAUSAS
    # =========================
    elif st.session_state.vista == "causas":

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        st.title("🧠 Causas")

        if "Producto" in df.columns:

            df_c = df.groupby("Producto")["Ventas"].sum().reset_index()
            df_c = df_c.sort_values("Ventas", ascending=False)

            st.subheader("📊 Productos más relevantes")
            st.dataframe(df_c)

            fig = px.bar(df_c.head(10), x="Producto", y="Ventas")
            st.plotly_chart(fig, use_container_width=True)

            df_t = df.groupby(["Periodo", "Producto"])["Ventas"].sum().reset_index()

            insights = []

            for prod, g in df_t.groupby("Producto"):
                g = g.sort_values("Periodo")

                if len(g) >= 2 and g.iloc[-2]["Ventas"] != 0:

                    v1 = g.iloc[-2]["Ventas"]
                    v2 = g.iloc[-1]["Ventas"]
                    var = (v2 - v1) / v1

                    if var < -0.15:
                        insights.append(f"🔴 Caída fuerte en {prod} ({var*100:.1f}%)")
                    elif var > 0.15:
                        insights.append(f"🟢 Crecimiento fuerte en {prod} ({var*100:.1f}%)")

            st.subheader("📌 Insights automáticos")

            if insights:
                for i in insights:
                    st.write(i)
            else:
                st.info("Sin cambios relevantes")

    # =========================
    # RESUMEN EJECUTIVO (COMPLETO)
    # =========================
    elif st.session_state.vista == "resumen":

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        st.title("🧠 Resumen Ejecutivo")

        st.subheader("📊 KPIs")
        c1, c2, c3 = st.columns(3)
        c1.metric("Ventas Totales", f"${ventas:,.0f}")
        c2.metric("Ganancia Total", f"${ganancia:,.0f}")
        c3.metric("Margen", f"{margen:.1f}%")

        st.subheader("📈 Tendencia")
        fig = px.line(df_m, x="Periodo", y="Ventas", markers=True)
        st.plotly_chart(fig, use_container_width=True)

        if len(df_m) > 1:
            crecimiento = df_m["Ventas"].pct_change().mean()
            if crecimiento > 0.05:
                st.success(f"🟢 Crecimiento promedio ({crecimiento*100:.1f}%)")
            elif crecimiento < -0.05:
                st.error(f"🔴 Caída promedio ({crecimiento*100:.1f}%)")
            else:
                st.warning(f"🟡 Estabilidad ({crecimiento*100:.1f}%)")

        st.subheader("🚦 Estado del negocio")
        if margen > 20 and ratio < 0.2:
            st.success("Negocio saludable")
        elif margen > 10:
            st.warning("Negocio aceptable")
        else:
            st.error("Negocio en riesgo")

        st.subheader("🧠 Insights")

        if len(df_m) >= 2:
            v1 = df_m.iloc[-2]["Ventas"]
            v2 = df_m.iloc[-1]["Ventas"]

            if v1 != 0:
                var = (v2 - v1) / v1
                st.write(f"Variación reciente: {var*100:.1f}%")

        if "Producto" in df.columns:
            top = df.groupby("Producto")["Ventas"].sum().idxmax()
            st.write(f"Producto líder: {top}")

        st.subheader("🔮 Proyección")

        if len(df_m) > 2:
            tendencia = df_m["Ventas"].diff().mean()
            proy = df_m["Ventas"].iloc[-1] + tendencia

            df_m["Proyección"] = df_m["Ventas"]
            df_m.loc[df_m.index[-1], "Proyección"] = proy

            fig2 = px.line(df_m, x="Periodo", y=["Ventas", "Proyección"], markers=True)
            st.plotly_chart(fig2, use_container_width=True)

    # =========================
    # RECOMENDACIONES (NO SE TOCA, SOLO MEJORADA)
    # =========================
    elif st.session_state.vista == "recomendaciones":

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        st.title("📌 Recomendaciones Estratégicas")

        recomendaciones = []

        def generar(df, col):
            df_t = df.groupby(["Periodo", col])["Ventas"].sum().reset_index()
            df_t["Periodo"] = pd.to_datetime(df_t["Periodo"])
            df_t = df_t.sort_values("Periodo")

            for k, g in df_t.groupby(col):
                if len(g) >= 2 and g.iloc[-2]["Ventas"] != 0:
                    v1 = g.iloc[-2]["Ventas"]
                    v2 = g.iloc[-1]["Ventas"]

                    var = (v2 - v1) / v1
                    impacto = abs((v2 - v1)) * v2

                    if var < -0.10:
                        recomendaciones.append({"tipo": "rojo","dimension": col,"nombre": k,"var": var,"impacto": impacto})
                    elif var > 0.10:
                        recomendaciones.append({"tipo": "verde","dimension": col,"nombre": k,"var": var,"impacto": impacto})

        for dim in ["Pais", "Region", "Canal", "Producto"]:
            if dim in df.columns:
                generar(df, dim)

        recomendaciones = sorted(recomendaciones, key=lambda x: (x["tipo"] == "verde", -x["impacto"]))

        for rec in recomendaciones:

            if rec["tipo"] == "verde":
                st.success(f"🟢 Escalar {rec['dimension']}: {rec['nombre']} ({rec['var']*100:.1f}%)")
            else:
                st.error(f"🔴 Recuperar {rec['dimension']}: {rec['nombre']} ({rec['var']*100:.1f}%)")

            st.caption(f"Impacto: ${rec['impacto']:,.0f}")

            with st.expander("📊 Ver gráfica"):
                df_f = df[df[rec["dimension"]] == rec["nombre"]]
                df_g = df_f.groupby("Periodo")["Ventas"].sum().reset_index()
                df_total = df.groupby("Periodo")["Ventas"].sum().reset_index()

                fig = px.line()
                fig.add_scatter(x=df_g["Periodo"], y=df_g["Ventas"], mode='lines+markers', name=rec["nombre"])
                fig.add_scatter(x=df_total["Periodo"], y=df_total["Ventas"], mode='lines+markers', name="Total", line=dict(dash='dash'))

                st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")

    # =========================
    # DETALLE
    # =========================
    elif st.session_state.vista == "detalle":

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        st.title("🔎 Análisis Detallado")
        st.info("Módulo en construcción")

else:
    st.info("📂 Sube archivo")
