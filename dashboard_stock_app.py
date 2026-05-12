import streamlit as st
import pandas as pd
import sqlite3
import base64
import os

from sigem_db import get_db_path
from dashboard_stock_app import dashboard_stock_app

from alertas_app import (
    dashboard_criticos,
    sin_stock_app,
    riesgo_alto_app,
    proximos_agotarse_app,
    detalle_criticos_app
)

from sobrestock_app import (
    dashboard_sobrestock,
    mayor_exceso_app,
    capital_detenido_app,
    detalle_sobrestock_app
)

from rotacion_app import (
    dashboard_rotacion,
    top_vendidos_app,
    baja_rotacion_app,
    entradas_salidas_app,
    detalle_rotacion_app
)

from ui_components import card_kpi


def aplicar_css():
    st.markdown("""
    <style>
    div.stButton > button {
        width: 100%;
        height: 70px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 12px;
        border: none;
        background-color: #1f77b4;
        color: white;
    }
    div.stButton > button:hover {
        background-color: #145a86;
    }
    </style>
    """, unsafe_allow_html=True)


def set_bg():
    if not os.path.exists("imagen8.png"):
        return

    with open("imagen8.png", "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(
            rgba(255,255,255,0.85),
            rgba(255,255,255,0.85)
        ),
        url("data:image/png;base64,{encoded}");
        background-size: cover;
    }}
    </style>
    """, unsafe_allow_html=True)


def cargar_datos_stock():

    conn = sqlite3.connect(get_db_path("inventarios"))

    materiales_path = get_db_path("materiales")

    conn.execute(f"""
        ATTACH DATABASE '{materiales_path}' AS materiales_db
    """)

    query = """
        SELECT
            m.codigo_material AS NUMERO_PRODUCTO,
            m.codigo_material AS codigo_material,
            m.descripcion AS DESCRIPCION,
            m.descripcion AS descripcion,
            m.descripcion_larga,
            m.categoria,
            m.familia,
            m.marca,
            m.tipo_material,
            m.unidad_base,
            COALESCE(m.stock_minimo, 0) AS STOCK_MIN,
            COALESCE(m.stock_maximo, 0) AS STOCK_MAX,
            COALESCE(m.stock_minimo, 0) AS stock_minimo,
            COALESCE(m.stock_maximo, 0) AS stock_maximo,
            COALESCE(m.costo_estandar, 0) AS costo_estandar,
            COALESCE(m.precio_venta, 0) AS precio_venta,
            COALESCE(m.rotacion_abc, '') AS rotacion_abc,

            COALESCE(SUM(
                CASE 
                    WHEN i.cantidad > 0 THEN i.cantidad
                    ELSE 0
                END
            ), 0) AS ENTRADA,

            COALESCE(SUM(
                CASE 
                    WHEN i.cantidad < 0 THEN ABS(i.cantidad)
                    ELSE 0
                END
            ), 0) AS SALIDA,

            COALESCE(SUM(i.cantidad), 0) AS STOCK

        FROM materiales_db.materiales m

        LEFT JOIN movimientos_inventario i
            ON m.codigo_material = i.codigo_material

        GROUP BY
            m.codigo_material,
            m.descripcion,
            m.descripcion_larga,
            m.categoria,
            m.familia,
            m.marca,
            m.tipo_material,
            m.unidad_base,
            m.stock_minimo,
            m.stock_maximo,
            m.costo_estandar,
            m.precio_venta,
            m.rotacion_abc

        ORDER BY m.codigo_material
    """

    try:
        df = pd.read_sql_query(query, conn)
    except Exception as e:
        conn.close()
        st.error("❌ Error cargando datos de stock desde SQLite.")
        st.exception(e)
        return pd.DataFrame()

    conn.close()

    df["STOCK"] = pd.to_numeric(df["STOCK"], errors="coerce").fillna(0)
    df["ENTRADA"] = pd.to_numeric(df["ENTRADA"], errors="coerce").fillna(0)
    df["SALIDA"] = pd.to_numeric(df["SALIDA"], errors="coerce").fillna(0)
    df["STOCK_MIN"] = pd.to_numeric(df["STOCK_MIN"], errors="coerce").fillna(0)
    df["STOCK_MAX"] = pd.to_numeric(df["STOCK_MAX"], errors="coerce").fillna(0)

    return df


def calcular_metricas(df):

    metricas = {}

    metricas["total_stock"] = int(df["STOCK"].sum())
    metricas["criticos"] = df[df["STOCK"] < df["STOCK_MIN"]].shape[0]
    metricas["sobrestock"] = df[df["STOCK"] > df["STOCK_MAX"]].shape[0]

    metricas["rotacion"] = (
        df["SALIDA"].sum() / df["ENTRADA"].sum()
        if df["ENTRADA"].sum() != 0
        else 0
    )

    metricas["valor_inventario"] = (
        df["STOCK"] * df["costo_estandar"]
    ).sum()

    return metricas


def dashboard_general(df):

    st.title("📊 Dashboard General Stock")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Inventario",
        "Compras",
        "Ventas",
        "Finanzas",
        "Alertas"
    ])

    with tab1:
        st.subheader("📦 Resumen Inventario")

        m = calcular_metricas(df)

        c1, c2 = st.columns(2)

        with c1:
            card_kpi("📦 Stock Total", f"{m['total_stock']:,}", "#1f77b4")

        with c2:
            card_kpi("🚨 Críticos", m["criticos"], "#e74c3c")

        c3, c4 = st.columns(2)

        with c3:
            card_kpi("⚠️ Sobrestock", m["sobrestock"], "#f39c12")

        with c4:
            card_kpi("📈 Rotación", f"{m['rotacion']:.2f}", "#2ecc71")

        c5, c6 = st.columns(2)

        with c5:
            card_kpi("💰 Valor inventario", f"${m['valor_inventario']:,.2f}", "#27ae60")

        with c6:
            card_kpi("📊 Productos", len(df), "#34495e")

        st.divider()

        st.subheader("📋 Stock por material")

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    with tab2:
        st.info("🛒 Indicadores de compras en construcción.")

    with tab3:
        st.info("📤 Módulo Ventas en construcción.")

    with tab4:
        st.info("💰 Módulo Finanzas en construcción.")

    with tab5:
        st.info("🚨 Módulo Alertas en construcción.")


def inventarios_app():

    aplicar_css()
    set_bg()

    st.title("📊 Analítica de Inventarios / Stock")

    df = cargar_datos_stock()

    if df.empty:
        st.warning("⚠️ No hay datos de materiales o movimientos para mostrar.")
        return

    vista = st.session_state.get(
        "menu_inventarios",
        "📊 Dashboard General"
    )

    st.caption(f"Ruta: Inventarios / {vista}")

    if vista == "📊 Dashboard General":

        dashboard_general(df)

    elif vista == "🚨 Críticos":

        st.title("🚨 Módulo Críticos")

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Dashboard",
            "Sin Stock",
            "Riesgo Alto",
            "Próximos a Agotarse",
            "Detalle"
        ])

        with tab1:
            dashboard_criticos(df)

        with tab2:
            sin_stock_app(df)

        with tab3:
            riesgo_alto_app(df)

        with tab4:
            proximos_agotarse_app(df)

        with tab5:
            detalle_criticos_app(df)

    elif vista == "⚠️ Sobrestock":

        st.title("⚠️ Módulo Sobrestock")

        tab1, tab2, tab3, tab4 = st.tabs([
            "Dashboard",
            "Mayor Exceso",
            "Capital Detenido",
            "Detalle"
        ])

        with tab1:
            dashboard_sobrestock(df)

        with tab2:
            mayor_exceso_app(df)

        with tab3:
            capital_detenido_app(df)

        with tab4:
            detalle_sobrestock_app(df)

    elif vista == "🔄 Rotación":

        st.title("🔄 Módulo Rotación")

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Dashboard",
            "Top Vendidos",
            "Baja Rotación",
            "Entradas vs Salidas",
            "Detalle"
        ])

        with tab1:
            dashboard_rotacion(df)

        with tab2:
            top_vendidos_app(df)

        with tab3:
            baja_rotacion_app(df)

        with tab4:
            entradas_salidas_app(df)

        with tab5:
            detalle_rotacion_app(df)
            
    elif st.session_state.modulo_analitico == "inventarios":
            dashboard_stock_app()

    elif vista == "🤖 IA":

        st.title("🤖 IA Inventarios")
        st.info("Módulo de IA para inventarios en construcción.")
