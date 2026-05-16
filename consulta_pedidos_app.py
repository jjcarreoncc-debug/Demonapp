import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

from sigem_db import get_db_path


# =====================================================
# CONEXIONES
# =====================================================

def get_conn_logistica():

    conn = sqlite3.connect(
        get_db_path("logistica")
    )

    conn.row_factory = sqlite3.Row

    return conn


def get_conn_inventarios():

    conn = sqlite3.connect(
        get_db_path("inventarios")
    )

    conn.row_factory = sqlite3.Row

    return conn


# =====================================================
# UTILIDADES
# =====================================================

def tabla_existe(conn, tabla):

    try:

        df = pd.read_sql_query(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name = ?
            """,
            conn,
            params=(tabla,)
        )

        return not df.empty

    except Exception:

        return False


def obtener_pedidos_detalle():

    conn = get_conn_logistica()

    if not tabla_existe(conn, "pedidos") or not tabla_existe(conn, "detalle_pedido"):

        conn.close()

        return pd.DataFrame()

    try:

        df = pd.read_sql_query(
            """
            SELECT
                p.pedido,
                p.fecha,
                p.cliente,
                p.destino,
                p.estatus AS estatus_pedido,
                p.observaciones,
                d.codigo_material,
                d.descripcion,
                d.cantidad_pedida,
                d.bodega,
                d.ubicacion,
                d.peso,
                d.volumen
            FROM pedidos p
            LEFT JOIN detalle_pedido d
                ON p.pedido = d.pedido
            ORDER BY p.fecha DESC, p.pedido DESC
            """,
            conn
        )

    except Exception:

        df = pd.DataFrame()

    conn.close()

    return df


def obtener_inventario_sistema():

    conn = get_conn_inventarios()

    if not tabla_existe(conn, "movimientos_inventario"):

        conn.close()

        return pd.DataFrame(
            columns=[
                "codigo_material",
                "inventario_sistema"
            ]
        )

    try:

        df = pd.read_sql_query(
            """
            SELECT
                codigo_material,
                SUM(
                    CASE
                        WHEN UPPER(IFNULL(tipo_movimiento, '')) = 'ENTRADA'
                            THEN IFNULL(cantidad, 0)
                        WHEN UPPER(IFNULL(tipo_movimiento, '')) = 'SALIDA'
                            THEN IFNULL(cantidad, 0) * -1
                        ELSE 0
                    END
                ) AS inventario_sistema
            FROM movimientos_inventario
            GROUP BY codigo_material
            """,
            conn
        )

    except Exception:

        df = pd.DataFrame(
            columns=[
                "codigo_material",
                "inventario_sistema"
            ]
        )

    conn.close()

    return df


def obtener_inventario_reservado():

    conn = get_conn_inventarios()

    if not tabla_existe(conn, "reservas_inventario"):

        conn.close()

        return pd.DataFrame(
            columns=[
                "codigo_material",
                "inventario_reservado"
            ]
        )

    try:

        df = pd.read_sql_query(
            """
            SELECT
                codigo_material,
                SUM(IFNULL(cantidad_reservada, 0)) AS inventario_reservado
            FROM reservas_inventario
            WHERE IFNULL(estatus, '') IN (
                'Reservado',
                'Activo',
                'Pendiente'
            )
            GROUP BY codigo_material
            """,
            conn
        )

    except Exception:

        df = pd.DataFrame(
            columns=[
                "codigo_material",
                "inventario_reservado"
            ]
        )

    conn.close()

    return df


def preparar_consulta_pedidos():

    df_pedidos = obtener_pedidos_detalle()

    if df_pedidos.empty:

        return df_pedidos

    df_inv = obtener_inventario_sistema()
    df_res = obtener_inventario_reservado()

    df = df_pedidos.merge(
        df_inv,
        on="codigo_material",
        how="left"
    )

    df = df.merge(
        df_res,
        on="codigo_material",
        how="left"
    )

    df["cantidad_pedida"] = pd.to_numeric(
        df["cantidad_pedida"],
        errors="coerce"
    ).fillna(0)

    df["inventario_sistema"] = pd.to_numeric(
        df["inventario_sistema"],
        errors="coerce"
    ).fillna(0)

    df["inventario_reservado"] = pd.to_numeric(
        df["inventario_reservado"],
        errors="coerce"
    ).fillna(0)

    df["inventario_disponible"] = (
        df["inventario_sistema"] -
        df["inventario_reservado"]
    )

    df["diferencia"] = (
        df["inventario_disponible"] -
        df["cantidad_pedida"]
    )

    def decidir(row):

        estatus_pedido = str(
            row.get("estatus_pedido", "")
        ).strip().lower()

        if "asignado" in estatus_pedido:

            return "Asignado a entrega"

        if row["inventario_disponible"] >= row["cantidad_pedida"]:

            return "Disponible para entrega"

        if row["inventario_disponible"] > 0:

            return "Parcial / requiere decisión"

        return "Sin inventario"

    df["decision_operativa"] = df.apply(
        decidir,
        axis=1
    )

    return df


# =====================================================
# APP
# =====================================================

def consulta_pedidos_app():

    st.title("📋 Consulta de pedidos")

    st.caption(
        "Visualización operativa de pedidos generados por ventas contra inventario disponible."
    )

    st.divider()

    df = preparar_consulta_pedidos()

    if df.empty:

        st.warning(
            "No se encontraron pedidos para consultar."
        )

        st.info(
            "Verifica que existan las tablas pedidos y detalle_pedido en Logística."
        )

        return

    # =====================================================
    # FILTROS
    # =====================================================

    st.markdown("### 🔎 Filtros")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        clientes = sorted(
            df["cliente"].dropna().astype(str).unique().tolist()
        )

        cliente_sel = st.selectbox(
            "Cliente",
            ["Todos"] + clientes
        )

    with col2:

        pedidos = sorted(
            df["pedido"].dropna().astype(str).unique().tolist()
        )

        pedido_sel = st.selectbox(
            "Pedido",
            ["Todos"] + pedidos
        )

    with col3:

        estatus = sorted(
            df["estatus_pedido"].dropna().astype(str).unique().tolist()
        )

        estatus_sel = st.selectbox(
            "Estatus pedido",
            ["Todos"] + estatus
        )

    with col4:

        decisiones = sorted(
            df["decision_operativa"].dropna().astype(str).unique().tolist()
        )

        decision_sel = st.selectbox(
            "Decisión",
            ["Todos"] + decisiones
        )

    df_filtrado = df.copy()

    if cliente_sel != "Todos":

        df_filtrado = df_filtrado[
            df_filtrado["cliente"].astype(str) == cliente_sel
        ]

    if pedido_sel != "Todos":

        df_filtrado = df_filtrado[
            df_filtrado["pedido"].astype(str) == pedido_sel
        ]

    if estatus_sel != "Todos":

        df_filtrado = df_filtrado[
            df_filtrado["estatus_pedido"].astype(str) == estatus_sel
        ]

    if decision_sel != "Todos":

        df_filtrado = df_filtrado[
            df_filtrado["decision_operativa"].astype(str) == decision_sel
        ]

    st.divider()

    # =====================================================
    # INDICADORES
    # =====================================================

    pedidos_total = df_filtrado["pedido"].nunique()
    lineas_total = len(df_filtrado)

    disponibles = len(
        df_filtrado[
            df_filtrado["decision_operativa"] == "Disponible para entrega"
        ]
    )

    parciales = len(
        df_filtrado[
            df_filtrado["decision_operativa"] == "Parcial / requiere decisión"
        ]
    )

    sin_inv = len(
        df_filtrado[
            df_filtrado["decision_operativa"] == "Sin inventario"
        ]
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.metric("Pedidos", pedidos_total)

    with c2:
        st.metric("Líneas", lineas_total)

    with c3:
        st.metric("Listas", disponibles)

    with c4:
        st.metric("Parciales", parciales)

    with c5:
        st.metric("Sin inventario", sin_inv)

    st.divider()

    # =====================================================
    # GRÁFICOS
    # =====================================================

    st.markdown("### 📊 Visualización operativa")

    graf1, graf2 = st.columns(2)

    with graf1:

        resumen_decision = (
            df_filtrado
            .groupby("decision_operativa")["pedido"]
            .count()
            .reset_index()
            .rename(columns={"pedido": "lineas"})
        )

        if not resumen_decision.empty:

            st.bar_chart(
                resumen_decision,
                x="decision_operativa",
                y="lineas"
            )

    with graf2:

        top_faltantes = (
            df_filtrado[df_filtrado["diferencia"] < 0]
            .groupby(["codigo_material", "descripcion"])["diferencia"]
            .sum()
            .reset_index()
        )

        if not top_faltantes.empty:

            top_faltantes["faltante"] = top_faltantes["diferencia"] * -1

            top_faltantes = top_faltantes.sort_values(
                "faltante",
                ascending=False
            ).head(10)

            st.bar_chart(
                top_faltantes,
                x="codigo_material",
                y="faltante"
            )

        else:

            st.info(
                "No hay materiales con faltante en el filtro actual."
            )

    st.divider()

    # =====================================================
    # GRID PRINCIPAL
    # =====================================================

    st.markdown("### 📄 Base general de pedidos")

    columnas_grid = [
        "pedido",
        "fecha",
        "cliente",
        "destino",
        "estatus_pedido",
        "codigo_material",
        "descripcion",
        "cantidad_pedida",
        "inventario_sistema",
        "inventario_reservado",
        "inventario_disponible",
        "diferencia",
        "decision_operativa",
        "bodega",
        "ubicacion"
    ]

    columnas_grid = [
        c for c in columnas_grid
        if c in df_filtrado.columns
    ]

    st.dataframe(
        df_filtrado[columnas_grid],
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # =====================================================
    # DESCARGA
    # =====================================================

    csv = df_filtrado[columnas_grid].to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "📥 Descargar consulta pedidos CSV",
        data=csv,
        file_name=f"consulta_pedidos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )


if __name__ == "__main__":

    consulta_pedidos_app()
