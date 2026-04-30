# =========================
# IMPORTS
# =========================
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Ejecutivo", layout="wide")

# =========================
# SESSION
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
    # FILTROS
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

    # =========================
    # AGREGADOS
    # =========================
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
            st.warning(f"Media ({ratio:.2f})")
        else:
            st.success(f"Baja ({ratio:.2f})")

        st.plotly_chart(px.line(df_m, x="Periodo", y="Ventas"))

    # =========================
    # RESPONSABLES
    # =========================
    elif st.session_state.vista == "responsables":

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        if "Vendedor_Ruta" in df.columns:
            df_r = df.groupby("Vendedor_Ruta")["Ventas"].sum().reset_index()
            st.dataframe(df_r)

    # =========================
    # CAUSAS
    # =========================
    elif st.session_state.vista == "causas":

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        if "Producto" in df.columns:
            df_c = df.groupby("Producto")["Ventas"].sum().reset_index()
            st.dataframe(df_c)

    # =========================
    # RESUMEN EJECUTIVO (EXTENDIDO)
    # =========================
    elif st.session_state.vista == "resumen":

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        st.title("🧠 Resumen Ejecutivo")

        df_res = df.copy()

        c1, c2, c3 = st.columns(3)

        if "Canal" in df.columns:
            canal = c1.multiselect("Canal", df["Canal"].unique(), df["Canal"].unique())
            df_res = df_res[df_res["Canal"].isin(canal)]

        if "Vendedor_Ruta" in df.columns:
            ruta = c2.multiselect("Ruta", df["Vendedor_Ruta"].unique(), df["Vendedor_Ruta"].unique())
            df_res = df_res[df_res["Vendedor_Ruta"].isin(ruta)]

        if "Producto" in df.columns:
            prod = c3.multiselect("Producto", df["Producto"].unique(), df["Producto"].unique())
            df_res = df_res[df_res["Producto"].isin(prod)]

        df_m_res = df_res.groupby("Periodo")["Ventas"].sum().reset_index()
        df_m_res["Periodo_dt"] = pd.to_datetime(df_m_res["Periodo"])
        df_m_res = df_m_res.sort_values("Periodo_dt")

        if len(df_m_res) >= 2:

            v1 = df_m_res.iloc[-2]["Ventas"]
            v2 = df_m_res.iloc[-1]["Ventas"]

            if v1 != 0:

                var = (v2 - v1) / v1

                st.metric("Variación", f"{var*100:.1f}%")

                if var > 0.10:
                    st.success("🟢 Crecimiento fuerte")
                elif var < -0.10:
                    st.error("🔴 Caída fuerte")
                else:
                    st.warning("🟡 Estable")

                st.subheader("📊 Drivers detallados")

                tabla_total = []

                for dim in ["Canal", "Pais", "Region", "Producto", "Vendedor_Ruta"]:

                    if dim in df_res.columns:

                        df_t = df_res.groupby(["Periodo", dim])["Ventas"].sum().reset_index()
                        df_t["Periodo"] = pd.to_datetime(df_t["Periodo"])

                        for k, g in df_t.groupby(dim):

                            if len(g) >= 2 and g.iloc[-2]["Ventas"] != 0:

                                v1_d = g.iloc[-2]["Ventas"]
                                v2_d = g.iloc[-1]["Ventas"]

                                var_d = (v2_d - v1_d) / v1_d

                                tabla_total.append([dim, k, v1_d, v2_d, var_d])

                df_tabla = pd.DataFrame(tabla_total, columns=["Dimensión", "Elemento", "Anterior", "Actual", "Variación"])

                st.dataframe(df_tabla)

                st.subheader("📈 Top crecimiento")
                st.dataframe(df_tabla.sort_values("Variación", ascending=False).head(5))

                st.subheader("📉 Top caída")
                st.dataframe(df_tabla.sort_values("Variación").head(5))

                # PROYECCIÓN
                proy = v2 * (1 + var)

                df_proj = df_m_res.copy()
                sig = df_proj["Periodo_dt"].iloc[-1] + pd.DateOffset(months=1)

                df_proj = pd.concat([
                    df_proj,
                    pd.DataFrame({
                        "Periodo": [sig.strftime("%Y-%m")],
                        "Ventas": [proy]
                    })
                ])

                st.plotly_chart(px.line(df_proj, x="Periodo", y="Ventas", markers=True))

    # =========================
    # RECOMENDACIONES
    # =========================
    elif st.session_state.vista == "recomendaciones":

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        st.title("📌 Recomendaciones (sin cambios)")

    # =========================
    # DETALLE
    # =========================
    elif st.session_state.vista == "detalle":

        if st.button("⬅️ Volver"):
            st.session_state.vista = "principal"

        st.dataframe(df)

else:
    st.info("📂 Sube archivo")
