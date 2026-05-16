import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

from sigem_db import get_db_path


def get_conn_logistica():
    conn = sqlite3.connect(get_db_path("logistica"))
    conn.row_factory = sqlite3.Row
    return conn


def get_conn_inventarios():
    conn = sqlite3.connect(get_db_path("inventarios"))
    conn.row_factory = sqlite3.Row
    return conn


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

            ORDER BY
                p.fecha DESC,
                p.pedido DESC
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

                        WHEN UPPER(
                            IFNULL(tipo_movimiento, '')
                        ) LIKE 'ENTRADA%'

                        THEN IFNULL(cantidad, 0)

                        WHEN UPPER(
                            IFNULL(tipo_movimiento, '')
                        ) LIKE 'SALIDA%'

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


# ============================================================
# INVENTARIO RESERVADO
# ============================================================
def obtener_inventario_reservado():

    conn = get_conn_inventarios()

    if not tabla_existe(conn, "movimientos_inventario"):
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

                SUM(
                    IFNULL(cantidad, 0)
                ) AS inventario_reservado

            FROM movimientos_inventario

            WHERE UPPER(
                IFNULL(tipo_movimiento, '')
            ) = 'RESERVA'

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

    for col in [
        "cantidad_pedida",
        "inventario_sistema",
        "inventario_reservado"
    ]:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        ).fillna(0)

    df["inventario_disponible"] = (
        df["inventario_sistema"]
        -
        df["inventario_reservado"]
    )

    df["diferencia"] = (
        df["inventario_disponible"]
        -
        df["cantidad_pedida"]
    )

    def decidir(row):

        estatus_pedido = str(
            row.get(
                "estatus_pedido",
                ""
            )
        ).strip().lower()

        if "asignado" in estatus_pedido:
            return "Asignado a entrega"

        if "cerrado" in estatus_pedido:
            return "Cerrado"

        if "cancelado" in estatus_pedido:
            return "Cancelado"

        if row["inventario_disponible"] >= row["cantidad_pedida"]:
            return "Disponible para entrega"

        if row["inventario_disponible"] > 0:
            return "Parcial / requiere decisión"

        return "Sin inventario"

    df["decision_operativa"] = df.apply(
        decidir,
        axis=1
    )

    def semaforo(row):

        decision = row["decision_operativa"]

        if decision == "Disponible para entrega":
            return "🟢 Listo"

        if decision == "Parcial / requiere decisión":
            return "🟡 Parcial"

        if decision == "Sin inventario":
            return "🔴 Sin inventario"

        if decision == "Asignado a entrega":
            return "🔵 Asignado"

        return "⚪ Revisar"

    df["semaforo"] = df.apply(
        semaforo,
        axis=1
    )

    return df


def columnas_grid_base():

    return [
        "semaforo",
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


def mostrar_grid(df, titulo):

    st.markdown(f"### {titulo}")

    columnas = [
        c
        for c in columnas_grid_base()
        if c in df.columns
    ]

    st.dataframe(
        df[columnas],
        use_container_width=True,
        hide_index=True
    )

    return columnas


def mostrar_indicadores(df):

    pedidos_total = df["pedido"].nunique()
    lineas_total = len(df)

    disponibles = len(
        df[
            df["decision_operativa"] == "Disponible para entrega"
        ]
    )

    parciales = len(
        df[
            df["decision_operativa"] == "Parcial / requiere decisión"
        ]
    )

    sin_inv = len(
        df[
            df["decision_operativa"] == "Sin inventario"
        ]
    )

    asignados = len(
        df[
            df["decision_operativa"] == "Asignado a entrega"
        ]
    )

    c1, c2, c3, c4, c5, c6 = st.columns(6)

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

    with c6:
        st.metric("Asignadas", asignados)


def mostrar_detalle_pedido(df):

    pedidos = sorted(
        df["pedido"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    if not pedidos:
        st.warning(
            "No existen pedidos en el filtro actual."
        )
        return

    pedido_sel = st.selectbox(
        "Selecciona pedido para ver detalle",
        pedidos,
        key="detalle_pedido_sel"
    )

    df_pedido = df[
        df["pedido"].astype(str) == pedido_sel
    ].copy()

    if df_pedido.empty:
        st.warning(
            "No se encontró detalle para el pedido seleccionado."
        )
        return

    encabezado = df_pedido.iloc[0]

    st.markdown(
        "### 🧾 Encabezado del pedido"
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Pedido",
            encabezado.get("pedido", "")
        )

    with c2:
        st.metric(
            "Cliente",
            encabezado.get("cliente", "")
        )

    with c3:
        st.metric(
            "Destino",
            encabezado.get("destino", "")
        )

    with c4:
        st.metric(
            "Estatus",
            encabezado.get("estatus_pedido", "")
        )

    st.info(
        f"Observaciones: {encabezado.get('observaciones', '')}"
    )

    mostrar_grid(
        df_pedido,
        "📦 Detalle operativo del pedido"
    )

    st.markdown(
        "### 📊 Resumen del pedido"
    )

    faltante_total = abs(
        df_pedido[
            df_pedido["diferencia"] < 0
        ]["diferencia"].sum()
    )

    r1, r2, r3, r4 = st.columns(4)

    with r1:
        st.metric(
            "Líneas",
            len(df_pedido)
        )

    with r2:
        st.metric(
            "Cantidad pedida",
            df_pedido["cantidad_pedida"].sum()
        )

    with r3:
        st.metric(
            "Disponible",
            df_pedido["inventario_disponible"].sum()
        )

    with r4:
        st.metric(
            "Faltante",
            faltante_total
        )


def mostrar_comparativos(df):

    st.markdown(
        "### 📊 Comparativos operación"
    )

    c1, c2 = st.columns(2)

    with c1:

        resumen_decision = (
            df.groupby("decision_operativa")["pedido"]
            .count()
            .reset_index()
            .rename(columns={"pedido": "lineas"})
        )

        if not resumen_decision.empty:

            st.markdown(
                "#### Líneas por decisión"
            )

            st.bar_chart(
                resumen_decision,
                x="decision_operativa",
                y="lineas"
            )

    with c2:

        resumen_cliente = (
            df.groupby("cliente")["pedido"]
            .nunique()
            .reset_index()
            .rename(columns={"pedido": "pedidos"})
            .sort_values("pedidos", ascending=False)
            .head(10)
        )

        if not resumen_cliente.empty:

            st.markdown(
                "#### Pedidos por cliente"
            )

            st.bar_chart(
                resumen_cliente,
                x="cliente",
                y="pedidos"
            )

    c3, c4 = st.columns(2)

    with c3:

        top_faltantes = (
            df[
                df["diferencia"] < 0
            ]
            .groupby(
                [
                    "codigo_material",
                    "descripcion"
                ]
            )["diferencia"]
            .sum()
            .reset_index()
        )

        if not top_faltantes.empty:

            top_faltantes["faltante"] = (
                top_faltantes["diferencia"] * -1
            )

            top_faltantes = (
                top_faltantes
                .sort_values("faltante", ascending=False)
                .head(10)
            )

            st.markdown(
                "#### Top materiales faltantes"
            )

            st.bar_chart(
                top_faltantes,
                x="codigo_material",
                y="faltante"
            )

        else:

            st.info(
                "No hay materiales con faltante."
            )

    with c4:

        demanda_material = (
            df.groupby(
                [
                    "codigo_material",
                    "descripcion"
                ]
            )["cantidad_pedida"]
            .sum()
            .reset_index()
            .sort_values(
                "cantidad_pedida",
                ascending=False
            )
            .head(10)
        )

        if not demanda_material.empty:

            st.markdown(
                "#### Top demanda por material"
            )

            st.bar_chart(
                demanda_material,
                x="codigo_material",
                y="cantidad_pedida"
            )


def consulta_pedidos_app():

    st.title("📋 Consulta de pedidos")

    st.caption(
        "Vista operativa de pedidos de ventas contra inventario disponible para decidir entregas."
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

    st.markdown(
        "### 🔎 Filtros generales"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        clientes = sorted(
            df["cliente"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        cliente_sel = st.selectbox(
            "Cliente",
            ["Todos"] + clientes
        )

    with col2:

        pedidos = sorted(
            df["pedido"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        pedido_sel = st.selectbox(
            "Pedido",
            ["Todos"] + pedidos
        )

    with col3:

        estatus = sorted(
            df["estatus_pedido"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        estatus_sel = st.selectbox(
            "Estatus pedido",
            ["Todos"] + estatus
        )

    with col4:

        decisiones = sorted(
            df["decision_operativa"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
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

    mostrar_indicadores(df_filtrado)

    st.divider()

    (
        tab_general,
        tab_detalle,
        tab_pendientes,
        tab_listos,
        tab_sin_inv,
        tab_comparativos
    ) = st.tabs(
        [
            "📄 Vista general",
            "📦 Detalle pedido",
            "⏳ Pendientes / parciales",
            "✅ Listos",
            "⚠️ Sin inventario",
            "📊 Comparativos"
        ]
    )

    with tab_general:

        columnas = mostrar_grid(
            df_filtrado,
            "Base general de pedidos"
        )

        st.download_button(
            "📥 Descargar vista general CSV",
            data=df_filtrado[columnas]
            .to_csv(index=False)
            .encode("utf-8"),
            file_name=f"consulta_pedidos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with tab_detalle:

        mostrar_detalle_pedido(df_filtrado)

    with tab_pendientes:

        df_pendientes = df_filtrado[
            df_filtrado["decision_operativa"] == "Parcial / requiere decisión"
        ].copy()

        if df_pendientes.empty:

            st.success(
                "No hay pedidos parciales o pendientes de decisión en el filtro actual."
            )

        else:

            mostrar_grid(
                df_pendientes,
                "Pedidos pendientes / parciales"
            )

    with tab_listos:

        df_listos = df_filtrado[
            df_filtrado["decision_operativa"] == "Disponible para entrega"
        ].copy()

        if df_listos.empty:

            st.info(
                "No hay pedidos listos para entrega en el filtro actual."
            )

        else:

            mostrar_grid(
                df_listos,
                "Pedidos listos para crear entrega"
            )

    with tab_sin_inv:

        df_sin_inv = df_filtrado[
            df_filtrado["decision_operativa"] == "Sin inventario"
        ].copy()

        if df_sin_inv.empty:

            st.success(
                "No hay pedidos sin inventario en el filtro actual."
            )

        else:

            mostrar_grid(
                df_sin_inv,
                "Pedidos sin inventario"
            )

    with tab_comparativos:

        mostrar_comparativos(df_filtrado)


if __name__ == "__main__":
    consulta_pedidos_app()
