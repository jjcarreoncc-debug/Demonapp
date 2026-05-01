import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os


st.set_page_config(page_title="Dashboard Ejecutivo", layout="wide")

if "vista" not in st.session_state:
    st.session_state.vista = "principal"

    

    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df = df.dropna(subset=["Fecha"])
# =========================
# CARGA DE DATOS PRINCIPAL
# =========================
archivo = st.sidebar.file_uploader("📂 Sube tu archivo Excel", type=["xlsx"])

if not archivo:
    st.warning("Sube un archivo para continuar")
    st.stop()

df = pd.read_excel(archivo)
    

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

        # 🔥 SOLO agregamos una columna adicional
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)

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

        # ✅ NUEVO NIVEL 5
        if col7.button("📊 Resultados"):
            st.session_state.vista = "resultados"
        
    # =========================
    # RESULTADOS (NUEVO)
    # =========================
    elif st.session_state.vista == "resultados":

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        st.title("📊 Resultados y Acciones Prioritarias")

        resultados = []

        for dim in ["Pais", "Region", "Canal", "Producto"]:
            if dim in df.columns:

                df_t = df.groupby(["Periodo", dim])["Ventas"].sum().reset_index()
                df_t = df_t.sort_values("Periodo")

                for k, g in df_t.groupby(dim):

                    if len(g) >= 2 and g.iloc[-2]["Ventas"] != 0:

                        v1 = g.iloc[-2]["Ventas"]
                        v2 = g.iloc[-1]["Ventas"]

                        var = (v2 - v1) / v1
                        impacto = (v2 - v1)

                        if abs(var) > 0.10:
                            resultados.append((dim, k, var, impacto, v1, v2))

        resultados = sorted(resultados, key=lambda x: abs(x[3]), reverse=True)

        for dim, nombre, var, impacto, v1, v2 in resultados:

            if var > 0:
                st.success(f"🟢 Oportunidad: {dim} → {nombre}")
                st.markdown("👉 Acción: escalar inversión / replicar estrategia")
            else:
                st.error(f"🔴 Riesgo: {dim} → {nombre}")
                st.markdown("👉 Acción: corregir ejecución / revisar causa")

            st.markdown(f"""
            - Antes: ${v1:,.0f}  
            - Ahora: ${v2:,.0f}  
            - Impacto: ${impacto:,.0f}  
            - Variación: {var*100:.1f}%
            """)

            st.markdown("---")

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

    # =========================
    # RESPONSABLES
    # =========================
    elif st.session_state.vista == "responsables":

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        st.title("👤 Responsables")

        if "Vendedor_Ruta" in df.columns:
            df_r = df.groupby("Vendedor_Ruta")["Ventas"].sum().reset_index()
            st.dataframe(df_r)

    # =========================
    # CAUSAS
    # =========================
    elif st.session_state.vista == "causas":

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        st.title("🧠 Causas")

        if "Producto" in df.columns:
            df_c = df.groupby("Producto")["Ventas"].sum().reset_index()
            st.dataframe(df_c)

    # =========================
    # RESUMEN
    # =========================
    elif st.session_state.vista == "resumen":

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        st.title("🧠 Resumen Ejecutivo")

        st.subheader("📈 Proyección")

        if len(df_m) > 2:
            tendencia = df_m["Ventas"].diff().mean()
            df_m["Proyección"] = df_m["Ventas"].iloc[-1] + tendencia

            fig = px.line(df_m, x="Periodo", y=["Ventas", "Proyección"], markers=True)
            st.plotly_chart(fig, use_container_width=True)

        def color_valores(val):
            try:
                val = float(val)
                if val < 0:
                    return 'color: red'
                elif val > 0:
                    return 'color: green'
            except:
                return ''
            return ''

        def format_color(val, tipo):
            try:
                val = float(val)
                if tipo == "var":
                    return f"🔴 {val:.2%}" if val < 0 else f"🟢 {val:.2%}"
                elif tipo == "money":
                    return f"🔴 ${val:,.0f}" if val < 0 else f"🟢 ${val:,.0f}"
            except:
                return val
            return val

        st.markdown("## 📊 Análisis adicional de desempeño")

        df_res = df.copy()
        tabla = []

        for dim in ["Canal", "Pais", "Region", "Producto"]:

            if dim in df_res.columns:

                df_t = df_res.groupby(["Periodo", dim])["Ventas"].sum().reset_index()
                df_t["Periodo"] = pd.to_datetime(df_t["Periodo"])
                df_t = df_t.sort_values("Periodo")

                for k, g in df_t.groupby(dim):

                    if len(g) >= 2 and g.iloc[-2]["Ventas"] != 0:

                        v1 = g.iloc[-2]["Ventas"]
                        v2 = g.iloc[-1]["Ventas"]

                        var = (v2 - v1) / v1
                        impacto = (v2 - v1)

                        estado = "Crece" if var > 0 else "Cae"

                        tabla.append([dim, k, v1, v2, var, impacto, estado])

        df_tabla = pd.DataFrame(
            tabla,
            columns=["Dimensión", "Elemento", "Anterior", "Actual", "Variación", "Impacto $", "Estado"]
        )

        if not df_tabla.empty:

            df_display = df_tabla.copy()
            df_display["Variación"] = df_display["Variación"].apply(lambda x: format_color(x, "var"))
            df_display["Impacto $"] = df_display["Impacto $"].apply(lambda x: format_color(x, "money"))

            st.dataframe(df_display)

   
    # =========================
    # RECOMENDACIONES (FULL)
    # =========================


    if st.button("⬅️ Volver"):
        st.session_state.vista = "principal"

    st.title("📌 Recomendaciones Estratégicas")

    recomendaciones = []

    def generar(df, col):

        df_t = df.groupby(["Periodo", col])["Ventas"].sum().reset_index()
        df_t = df_t.sort_values("Periodo")

        detalle_crece = []
        detalle_cae = []

        for k, g in df_t.groupby(col):

            if len(g) >= 2 and g.iloc[-2]["Ventas"] != 0:

                v1 = g.iloc[-2]["Ventas"]
                v2 = g.iloc[-1]["Ventas"]

                var = (v2 - v1) / v1
                impacto = abs(v2 - v1)

                p1 = g.iloc[-2]["Periodo"]
                p2 = g.iloc[-1]["Periodo"]

                if var < -0.10:
                    recomendaciones.append((col, k, var, impacto, "rojo", v1, v2, p1, p2))
                    detalle_cae.append((k, var))

                elif var > 0.10:
                    recomendaciones.append((col, k, var, impacto, "verde", v1, v2, p1, p2))
                    detalle_crece.append((k, var))

        return detalle_crece, detalle_cae

    resumen_dim = {}

    for dim in ["Pais", "Region", "Canal", "Producto"]:
        if dim in df.columns:
            crece, cae = generar(df, dim)
            resumen_dim[dim] = {"crece": crece, "cae": cae}

    recomendaciones = sorted(recomendaciones, key=lambda x: x[3], reverse=True)

    for dim, nombre, var, impacto, tipo, v1, v2, p1, p2 in recomendaciones:

        if tipo == "verde":
            st.success(f"🟢 Escalar {dim}: {nombre} ({var*100:.1f}%)")
        else:
            st.error(f"🔴 Recuperar {dim}: {nombre} ({var*100:.1f}%)")

        st.markdown(f"""
        - Periodo anterior ({p1}): ${v1:,.0f}  
        - Periodo actual ({p2}): ${v2:,.0f}  
        - Impacto: ${impacto:,.0f}  
        - Variación: {var*100:.1f}%
        """)

        df_det = df[df[dim] == nombre]

        # DRIVER PRINCIPAL
        for subdim in ["Producto", "Region", "Canal"]:
            if subdim in df_det.columns and subdim != dim:
                top = df_det.groupby(subdim)["Ventas"].sum().reset_index() \
                            .sort_values("Ventas", ascending=False).head(1)

                if not top.empty:
                    st.info(
                        f"Driver principal: {subdim} → {top.iloc[0][subdim]} "
                        f"(${top.iloc[0]['Ventas']:,.0f})"
                    )
                    break

        # DETALLE
        with st.expander("🔍 Ver detalle"):

            for subdim in ["Producto", "Region", "Canal"]:
                if subdim in df_det.columns and subdim != dim:

                    df_sub = df_det.groupby(["Periodo", subdim])["Ventas"].sum().reset_index()
                    df_sub = df_sub.sort_values("Periodo")

                    tabla = []

                    for k2, g2 in df_sub.groupby(subdim):

                        if len(g2) >= 2 and g2.iloc[-2]["Ventas"] != 0:

                            a1 = g2.iloc[-2]["Ventas"]
                            a2 = g2.iloc[-1]["Ventas"]
                            var2 = (a2 - a1) / a1

                            tabla.append([k2, a1, a2, var2])

                    if tabla:
                        df_detalle = pd.DataFrame(
                            tabla,
                            columns=["Elemento", "Anterior", "Actual", "Variación"]
                        )

                        df_detalle["Variación"] = df_detalle["Variación"].apply(
                            lambda x: f"🔴 {x:.1%}" if x < 0 else f"🟢 {x:.1%}"
                        )

                        st.dataframe(df_detalle.head(5))

        # GRÁFICA + PROYECCIÓN
        with st.expander("📊 Ver gráfica con proyección"):

            df_f = df[df[dim] == nombre]
            df_g = df_f.groupby("Periodo")["Ventas"].sum().reset_index()

            if len(df_g) >= 2:

                df_g["Periodo_dt"] = pd.to_datetime(df_g["Periodo"])
                df_g = df_g.sort_values("Periodo_dt")

                v1g = df_g.iloc[-2]["Ventas"]
                v2g = df_g.iloc[-1]["Ventas"]

                if v1g != 0:
                    var_g = (v2g - v1g) / v1g
                    proy = v2g * (1 + var_g)

                    sig = df_g["Periodo_dt"].iloc[-1] + pd.DateOffset(months=1)

                    df_g = pd.concat([
                        df_g,
                        pd.DataFrame({
                            "Periodo": [sig.strftime("%Y-%m")],
                            "Ventas": [proy]
                        })
                    ])

            fig = px.line(df_g, x="Periodo", y="Ventas", markers=True)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")


# =========================
# DETALLE
# =========================
elif st.session_state.vista == "detalle":

    if st.button("⬅️ Volver"):
        st.session_state.vista = "principal"

    st.title("🔎 Análisis Detallado")
    st.dataframe(df)


# =========================
# ⚠️ SIEMPRE ÚLTIMO
# =========================
else:
    st.info("Selecciona una vista del dashboard")

