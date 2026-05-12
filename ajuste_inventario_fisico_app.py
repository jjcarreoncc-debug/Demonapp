import sqlite3
from datetime import datetime

import pandas as pd
import streamlit as st

from sigem_db import get_db_path


def obtener_conteos_contados():

    conn = sqlite3.connect(get_db_path("inventarios"))

    try:
        df = pd.read_sql_query("""
            SELECT
                id_conteo,
                folio_conteo,
                fecha_conteo,
                codigo_material,
                descripcion,
                bodega,
                ubicacion,
                cantidad_sistema,
                cantidad_fisica,
                diferencia,
                usuario,
                estatus
            FROM inventario_fisico
            WHERE estatus = 'Contado'
              AND diferencia <> 0
            ORDER BY id_conteo DESC
        """, conn)

    except Exception:
        df = pd.DataFrame()

    conn.close()
    return df


def aplicar_ajuste(id_conteo):

    conn = sqlite3.connect(get_db_path("inventarios"))
    cur = conn.cursor()

    cur.execute("""
        SELECT
            folio_conteo,
            codigo_material,
            descripcion,
            bodega,
            ubicacion,
            diferencia,
            cantidad_sistema,
            cantidad_fisica
        FROM inventario_fisico
        WHERE id_conteo = ?
    """, (id_conteo,))

    row = cur.fetchone()

    if row is None:
        conn.close()
        return False, "No se encontró el conteo."

    folio_conteo = row[0]
    codigo_material = row[1]
    descripcion = row[2]
    bodega = row[3]
    ubicacion = row[4]
    diferencia = float(row[5] or 0)

    cantidad_sistema = float(row[6] or 0)
    cantidad_fisica = float(row[7] or 0)

    if diferencia == 0:
        conn.close()
        return False, "El conteo no tiene diferencia."

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    folio_movimiento = (
        f"AJ-IF-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    )

    if diferencia > 0:

        tipo_movimiento = "ENTRADA_AJUSTE"

        tipo_ajuste = "ENTRADA"

        cantidad = diferencia

    else:

        tipo_movimiento = "SALIDA_AJUSTE"

        tipo_ajuste = "SALIDA"

        cantidad = abs(diferencia) * -1

    cur.execute("""
        INSERT INTO movimientos_inventario (
            folio_movimiento,
            fecha,
            tipo_movimiento,
            tipo_documento,
            numero_documento,
            archivo_documento,
            codigo_material,
            descripcion,
            cantidad,
            costo_unitario,
            total,
            bodega,
            ubicacion,
            referencia,
            comentarios,
            usuario
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        folio_movimiento,
        fecha,
        tipo_movimiento,
        "Inventario físico",
        folio_conteo,
        "",
        codigo_material,
        descripcion,
        cantidad,
        0,
        0,
        bodega,
        ubicacion,
        f"Ajuste por inventario físico {folio_conteo}",
        "Ajuste generado desde inventario físico",
        "supervisor"
    ))

    stock_anterior = cantidad_sistema

    stock_nuevo = cantidad_fisica

    cur.execute("""
        INSERT INTO ajustes_inventario (
            folio_ajuste,
            fecha,
            codigo_material,
            descripcion,
            tipo_ajuste,
            cantidad,
            stock_anterior,
            stock_nuevo,
            comentarios,
            usuario
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        folio_movimiento,
        fecha,
        codigo_material,
        descripcion,
        tipo_ajuste,
        abs(diferencia),
        stock_anterior,
        stock_nuevo,
        f"Ajuste generado desde conteo {folio_conteo}",
        "supervisor"
    ))

    cur.execute("""
        UPDATE inventario_fisico
        SET estatus = 'Ajustado'
        WHERE id_conteo = ?
    """, (id_conteo,))

    conn.commit()
    conn.close()

    return True, "Ajuste aplicado correctamente."


def ajuste_inventario_fisico_app():

    st.title("✅ Aplicar ajuste de inventario físico")

    st.caption(
        "Genera movimientos de ajuste a partir de conteos físicos contados."
    )

    df = obtener_conteos_contados()

    if df.empty:

        st.info(
            "No hay conteos contados con diferencia pendiente de ajuste."
        )

        return

    st.subheader("📋 Conteos pendientes de ajuste")

    st.dataframe(
        df,
        use_container_width=True
    )

    lista_conteos = df.apply(
        lambda row:
        f"{row['id_conteo']} | "
        f"{row['folio_conteo']} | "
        f"{row['codigo_material']} - "
        f"{row['descripcion']} | "
        f"Diferencia: {row['diferencia']}",
        axis=1
    ).tolist()

    conteo_sel = st.selectbox(
        "Selecciona conteo para ajustar",
        lista_conteos
    )

    id_conteo = int(
        conteo_sel.split("|")[0].strip()
    )

    row = df[df["id_conteo"] == id_conteo].iloc[0]

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Sistema",
            row["cantidad_sistema"]
        )

    with col2:
        st.metric(
            "Físico",
            row["cantidad_fisica"]
        )

    with col3:
        st.metric(
            "Diferencia",
            row["diferencia"]
        )

    if row["diferencia"] > 0:

        st.success(
            "Este ajuste generará una ENTRADA de inventario."
        )

    elif row["diferencia"] < 0:

        st.warning(
            "Este ajuste generará una SALIDA de inventario."
        )

    confirmar = st.checkbox(
        "Confirmo que deseo aplicar este ajuste de inventario"
    )

    if st.button(
        "✅ Aplicar ajuste",
        use_container_width=True
    ):

        if not confirmar:

            st.warning(
                "Debes confirmar antes de aplicar el ajuste."
            )

            return

        ok, mensaje = aplicar_ajuste(id_conteo)

        if ok:

            st.success(mensaje)

            st.rerun()

        else:

            st.error(mensaje)
