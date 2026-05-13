import streamlit as st
import pandas as pd
import sqlite3

from datetime import date

from sigem_db import get_db_path


# ==========================================
# TRAZABILIDAD
# ==========================================

def trazabilidad_app():

    st.title("🔎 Trazabilidad Inventario")

    st.markdown("---")


    # ==========================================
    # FILTROS
    # ==========================================

    col1, col2 = st.columns(2)

    with col1:
        fecha_inicio = st.date_input(
            "📅 Fecha inicio",
            value=date.today().replace(day=1)
        )

    with col2:
        fecha_fin = st.date_input(
            "📅 Fecha final",
            value=date.today()
        )


    # ==========================================
    # CONEXION DB
    # ==========================================

    db_path = get_db_path("inventarios")

    conn = sqlite3.connect(db_path)


    # ==========================================
    # CONSULTA
    # ==========================================

    query = """
        SELECT *
        FROM movimientos_inventario
        WHERE DATE(fecha_movimiento)
        BETWEEN ? AND ?
        ORDER BY fecha_movimiento DESC
    """


    try:

        df = pd.read_sql_query(
            query,
            conn,
            params=[fecha_inicio, fecha_fin]
        )

        # ==========================================
        # KPIs
        # ==========================================

        total_movimientos = len(df)

        entradas = len(
            df[df["tipo_movimiento"] == "ENTRADA"]
        ) if not df.empty else 0

        salidas = len(
            df[df["tipo_movimiento"] == "SALIDA"]
        ) if not df.empty else 0


        k1, k2, k3 = st.columns(3)

        with k1:
            st.metric(
                "Movimientos",
                total_movimientos
            )

        with k2:
            st.metric(
                "Entradas",
                entradas
            )

        with k3:
            st.metric(
                "Salidas",
                salidas
            )


        st.markdown("---")


        # ==========================================
        # TABLA
        # ==========================================

        st.subheader("📋 Historial movimientos")

        st.dataframe(
            df,
            use_container_width=True
        )


    except Exception as e:

        st.error(
            "Error consultando trazabilidad"
        )

        st.exception(e)

    finally:

        conn.close()
