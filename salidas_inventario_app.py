import streamlit as st
import pandas as pd
import sqlite3

from datetime import datetime
from sigem_db import get_db_path


def obtener_materiales():

    db_path = get_db_path("inventarios")
    conn = sqlite3.connect(db_path)

    try:
        query = """
            SELECT
                codigo_material,
                descripcion
            FROM materiales
            WHERE estatus = 'Activo'
            ORDER BY codigo_material
        """

        df = pd.read_sql(query, conn)

    except Exception as e:
        st.error("Error leyendo tabla materiales en inventarios.db")
        st.exception(e)
        df = pd.DataFrame()

    conn.close()
    return df


def obtener_existencia(codigo_material):

    db_path = get_db_path("inventarios")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        SELECT COALESCE(SUM(cantidad), 0)
        FROM movimientos_inventario
        WHERE codigo_material = ?
    """, (codigo_material,))

    existencia = cur.fetchone()[0]

    conn.close()
    return existencia


def registrar_movimiento(
    tipo_movimiento,
    codigo_material,
    descripcion,
    cantidad,
    referencia,
    comentarios
):

    db_path = get_db_path("inventarios")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO movimientos_inventario (
            fecha,
            tipo_movimiento,
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
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        tipo_movimiento,
        codigo_material,
        descripcion,
        cantidad,
        0,
        0,
        "",
        "",
        referencia,
        comentarios,
        st.session_state.get("usuario", "admin")
    ))

    conn.commit()
    conn.close()


def salidas_inventario_app():

    st.title("📤 SG201 - Salidas Inventario")

    materiales = obtener_materiales()

    if materiales.empty:
        st.warning("No existen materiales activos registrados en inventarios.db.")
        return

    st.subheader("🧾 Encabezado")

    c1, c2 = st.columns(2)

    with c1:
        referencia = st.selectbox(
            "Tipo salida",
            [
                "VENTA",
                "CONSUMO_INTERNO",
                "MERMA",
                "TRANSFERENCIA",
                "AJUSTE"
            ]
        )

    with c2:
        st.date_input("Fecha")

    comentarios = st.text_area("Comentarios")

    st.subheader("📦 Material")

    materiales["display"] = (
        materiales["codigo_material"].astype(str)
        + " - "
        + materiales["descripcion"].astype(str)
    )

    material_seleccionado = st.selectbox(
        "Selecciona material",
        materiales["display"]
    )

    material_info = materiales[
        materiales["display"] == material_seleccionado
    ].iloc[0]

    codigo_material = material_info["codigo_material"]
    descripcion = material_info["descripcion"]

    existencia = obtener_existencia(codigo_material)

    st.info(f"Existencia actual: {existencia}")

    cantidad = st.number_input(
        "Cantidad salida",
        min_value=0.0,
        step=1.0
    )

    if st.button("💾 Registrar salida"):

        if cantidad <= 0:
            st.error("Cantidad inválida.")
            return

        if cantidad > existencia:
            st.error("No existe stock suficiente.")
            return

        registrar_movimiento(
            "SALIDA",
            codigo_material,
            descripcion,
            cantidad * -1,
            referencia,
            comentarios
        )

        st.success("✅ Salida registrada correctamente")


if __name__ == "__main__":
    salidas_inventario_app()
