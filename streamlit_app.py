import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Ejecutivo", layout="wide")

# =========================
# ESTADO
# =========================
if "vista" not in st.session_state:
    st.session_state.vista = "principal"

archivo = st.file_uploader("📂 Sube tu archivo Excel", type=["xlsx"])

# =========================
# DATA
# =========================
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

    # =========================
    # FILTROS GENERALES
    # =========================
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
    df_m["Periodo_dt"] = pd.to_datetime(df_m["Periodo"])
    df_m = df_m.sort_values("Periodo_dt")

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

        if col4.button("🔎 Detalle"):
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

        fig = px.line(df_m, x="Periodo", y="Ventas", markers=True)
        st.plotly_chart(fig, use_container_width=True)

    # =========================
    # RESPONSABLES
    # =========================
    elif st.session_state.vista == "responsables":

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        st.title("👤 Responsables")

        if "Vendedor_Ruta" in df.columns:
            df_r = df.groupby("Vendedor_Ruta")["Ventas"].sum().reset_index().sort_values("Ventas", ascending=False)
            st.dataframe(df_r)

            fig = px.bar(df_r, x="Vendedor_Ruta", y="Ventas")
            st.plotly_chart(fig, use_container_width=True)

            top = df_r.head(3)["Vendedor_Ruta"]
            df_t = df[df["Vendedor_Ruta"].isin(top)]
            df_t = df_t.groupby(["Periodo", "Vendedor_Ruta"])["Ventas"].sum().reset_index()

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
            df_c = df.groupby("Producto")["Ventas"].sum().reset_index().sort_values("Ventas", ascending=False)
            st.dataframe(df_c)

            df_t = df.groupby(["Periodo", "Producto"])["Ventas"].sum().reset_index()

            for prod, g in df_t.groupby("Producto"):
                g = g.sort_values("Periodo")
                if len(g) >= 2 and g.iloc[-2]["Ventas"] != 0:
                    var = (g.iloc[-1]["Ventas"] - g.iloc[-2]["Ventas"]) / g.iloc[-2]["Ventas"]
                    if var < -0.15:
                        st.error(f"{prod} caída fuerte ({var*100:.1f}%)")
                    elif var > 0.15:
                        st.success(f"{prod} crecimiento fuerte ({var*100:.1f}%)")

    # =========================
    # RESUMEN EJECUTIVO
    # =========================
    elif st.session_state.vista == "resumen":

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        st.title("🧠 Resumen Ejecutivo")

        df_res = df.copy()

        colf1, colf2, colf3 = st.columns(3)

        if "Canal" in df.columns:
            canal = colf1.multiselect("Canal", df["Canal"].unique(), df["Canal"].unique())
            df_res = df_res[df_res["Canal"].isin(canal)]

        if "Vendedor_Ruta" in df.columns:
            ruta = colf2.multiselect("Ruta", df["Vendedor_Ruta"].unique(), df["Vendedor_Ruta"].unique())
            df_res = df_res[df_res["Vendedor_Ruta"].isin(ruta)]

        if "Producto" in df.columns:
            prod = colf3.multiselect("Producto", df["Producto"].unique(), df["Producto"].unique())
            df_res = df_res[df_res["Producto"].isin(prod)]

        df_m_res = df_res.groupby("Periodo")["Ventas"].sum().reset_index()
        df_m_res["Periodo_dt"] = pd.to_datetime(df_m_res["Periodo"])
        df_m_res = df_m_res.sort_values("Periodo_dt")

        if len(df_m_res) >= 2:

            v1 = df_m_res.iloc[-2]["Ventas"]
            v2 = df_m_res.iloc[-1]["Ventas"]

            if v1 != 0:

                var = (v2 - v1) / v1

                c1, c2, c3 = st.columns(3)
                c1.metric("Último periodo", f"${v2:,.0f}")
                c2.metric("Anterior", f"${v1:,.0f}")
                c3.metric("Variación", f"{var*100:.1f}%")

                if var > 0.10:
                    st.success("🟢 Crecimiento fuerte")
                elif var < -0.10:
                    st.error("🔴 Caída fuerte")
                else:
                    st.warning("🟡 Estable")

                proy = v2 * (1 + var)

                df_proj = df_m_res.copy()
                sig = df_proj["Periodo_dt"].iloc[-1] + pd.DateOffset(months=1)

                df_proj = pd.concat([
                    df_proj,
                    pd.DataFrame({
                        "Periodo": [sig.strftime("%Y-%m")],
                        "Ventas": [proy],
                        "Periodo_dt": [sig]
                    })
                ])

                fig = px.line(df_proj, x="Periodo", y="Ventas", markers=True)
                st.plotly_chart(fig, use_container_width=True)

    # =========================
    # RECOMENDACIONES
    # =========================
    elif st.session_state.vista == "recomendaciones":

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        st.title("📌 Recomendaciones")

        recomendaciones = []

        def generar(col):
            df_t = df.groupby(["Periodo", col])["Ventas"].sum().reset_index()
            df_t["Periodo"] = pd.to_datetime(df_t["Periodo"])
            df_t = df_t.sort_values("Periodo")

            for k, g in df_t.groupby(col):
                if len(g) >= 2 and g.iloc[-2]["Ventas"] != 0:
                    v1 = g.iloc[-2]["Ventas"]
                    v2 = g.iloc[-1]["Ventas"]

                    var = (v2 - v1) / v1
                    impacto = abs(v2 - v1)

                    if var < -0.10:
                        recomendaciones.append((f"🔴 Recuperar {col}: {k}", impacto))
                    elif var > 0.10:
                        recomendaciones.append((f"🟢 Escalar {col}: {k}", impacto))

        for dim in ["Pais", "Region", "Canal", "Producto"]:
            if dim in df.columns:
                generar(dim)

        recomendaciones = sorted(recomendaciones, key=lambda x: -x[1])

        for r, imp in recomendaciones:
            st.write(r)
            st.caption(f"Impacto: ${imp:,.0f}")
            st.markdown("---")

    # =========================
    # DETALLE
    # =========================
    elif st.session_state.vista == "detalle":

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        st.title("🔎 Detalle")
        st.dataframe(df)

else:
    st.info("📂 Sube archivo")
