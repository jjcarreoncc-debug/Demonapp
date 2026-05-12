import streamlit as st
import pandas as pd
import sqlite3
import re

from pathlib import Path
from datetime import datetime
from pypdf import PdfReader

from sigem_db import get_db_path


def obtener_catalogo_materiales():

    db_path = get_db_path("materiales")
    conn = sqlite3.connect(db_path)

    try:
        df = pd.read_sql("""
            SELECT
                codigo_material,
                descripcion
            FROM materiales
            WHERE estatus = 'Activo'
            ORDER BY codigo_material
        """, conn)

    except Exception:
        df = pd.DataFrame(columns=["codigo_material", "descripcion"])

    conn.close()
    return df


def crear_tablas_entrada_compras():

    db_path = get_db_path("compras")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS entradas_compras (
            id_entrada INTEGER PRIMARY KEY AUTOINCREMENT,
            proveedor TEXT,
            factura TEXT,
            fecha_factura TEXT,
            fecha_recepcion TEXT,
            moneda TEXT,
            tipo_cambio REAL,
            comentarios TEXT,
            archivo_adjunto TEXT,
            fecha_creacion TEXT,
            usuario_creacion TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS entradas_compras_detalle (
            id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
            id_entrada INTEGER,
            codigo_material TEXT,
            descripcion TEXT,
            cantidad REAL,
            costo_unitario REAL,
            impuesto REAL,
            total REAL,
            bodega TEXT,
            ubicacion TEXT
        )
    """)

    conn.commit()
    conn.close()


def crear_tabla_movimientos_inventario():

    db_path = get_db_path("inventarios")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS movimientos_inventario (
            id_movimiento INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            tipo_movimiento TEXT,
            codigo_material TEXT,
            descripcion TEXT,
            cantidad REAL,
            costo_unitario REAL,
            total REAL,
            bodega TEXT,
            ubicacion TEXT,
            referencia TEXT,
            comentarios TEXT,
            usuario TEXT
        )
    """)

    conn.commit()
    conn.close()


def registrar_movimiento_inventario(
    codigo_material,
    descripcion,
    cantidad,
    costo_unitario,
    total,
    bodega,
    ubicacion,
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
        "ENTRADA",
        codigo_material,
        descripcion,
        cantidad,
        costo_unitario,
        total,
        bodega,
        ubicacion,
        referencia,
        comentarios,
        st.session_state.get("usuario", "admin")
    ))

    conn.commit()
    

    st.success(
        f"Movimiento guardado: {codigo_material} / {cantidad}"
    )

    st.write(
        "BD inventarios:",
        get_db_path("inventarios")
    )

    conn.close()
    


def entrada_compras_app():

    st.title("📥 Entrada de Compras / Factura")

    crear_tablas_entrada_compras()
    crear_tabla_movimientos_inventario()

    catalogo = obtener_catalogo_materiales()

    if catalogo.empty:
        st.warning("No hay materiales activos registrados en el catálogo.")
        return

    opciones_materiales = [
        f"{row.codigo_material} - {row.descripcion}"
        for _, row in catalogo.iterrows()
    ]

    mapa_materiales = {
        f"{row.codigo_material} - {row.descripcion}": {
            "codigo_material": row.codigo_material,
            "descripcion": row.descripcion
        }
        for _, row in catalogo.iterrows()
    }

    st.subheader("🧾 Encabezado factura")

    c1, c2, c3 = st.columns(3)

    with c1:
        proveedor = st.text_input("Proveedor")
        factura = st.text_input("Factura")

    with c2:
        fecha_factura = st.date_input("Fecha factura")
        fecha_recepcion = st.date_input("Fecha recepción")

    with c3:
        moneda = st.selectbox("Moneda", ["MXN", "USD", "EUR"])
        tipo_cambio = st.number_input("Tipo cambio", value=1.0)

    comentarios = st.text_area("Comentarios")

    st.subheader("📦 Captura de materiales")

    if "detalle_compra_manual" not in st.session_state:
        st.session_state["detalle_compra_manual"] = []

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        material_sel = st.selectbox(
            "Material",
            opciones_materiales
        )

    material_data = mapa_materiales[material_sel]

    with c2:
        st.text_input(
            "Descripción",
            value=material_data["descripcion"],
            disabled=True
        )

    with c3:
        cantidad = st.number_input(
            "Cantidad / piezas",
            min_value=0.0,
            step=1.0
        )

    with c4:
        costo_unitario = st.number_input(
            "Costo unitario",
            min_value=0.0,
            step=1.0
        )

    impuesto = st.number_input(
        "Impuesto",
        min_value=0.0,
        step=1.0
    )

    bodega = st.text_input("Bodega")
    ubicacion = st.text_input("Ubicación")

    if st.button("➕ Agregar material"):

        if cantidad <= 0:
            st.error("La cantidad debe ser mayor a cero.")
            return

        total = (cantidad * costo_unitario) + impuesto

        st.session_state["detalle_compra_manual"].append({
            "codigo_material": material_data["codigo_material"],
            "descripcion": material_data["descripcion"],
            "cantidad": cantidad,
            "costo_unitario": costo_unitario,
            "impuesto": impuesto,
            "total": total,
            "bodega": bodega,
            "ubicacion": ubicacion
        })

        st.success("Material agregado a la entrada.")

    detalle = pd.DataFrame(st.session_state["detalle_compra_manual"])

    st.subheader("📋 Detalle de entrada")

    if not detalle.empty:
        st.dataframe(detalle, use_container_width=True)
    else:
        st.info("Agrega materiales para registrar la entrada.")

    if st.button("💾 Registrar entrada de compras"):

        if not proveedor or not factura:
            st.error("Proveedor y factura son obligatorios.")
            return

        if detalle.empty:
            st.error("Debes agregar al menos un material.")
            return

        db_path = get_db_path("compras")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO entradas_compras (
                proveedor,
                factura,
                fecha_factura,
                fecha_recepcion,
                moneda,
                tipo_cambio,
                comentarios,
                archivo_adjunto,
                fecha_creacion,
                usuario_creacion
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            proveedor,
            factura,
            str(fecha_factura),
            str(fecha_recepcion),
            moneda,
            tipo_cambio,
            comentarios,
            "",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            st.session_state.get("usuario", "admin")
        ))

        id_entrada = cur.lastrowid

        for _, row in detalle.iterrows():

            cur.execute("""
                INSERT INTO entradas_compras_detalle (
                    id_entrada,
                    codigo_material,
                    descripcion,
                    cantidad,
                    costo_unitario,
                    impuesto,
                    total,
                    bodega,
                    ubicacion
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                id_entrada,
                row["codigo_material"],
                row["descripcion"],
                float(row["cantidad"]),
                float(row["costo_unitario"]),
                float(row["impuesto"]),
                float(row["total"]),
                row["bodega"],
                row["ubicacion"]
            ))

            registrar_movimiento_inventario(
                codigo_material=row["codigo_material"],
                descripcion=row["descripcion"],
                cantidad=float(row["cantidad"]),
                costo_unitario=float(row["costo_unitario"]),
                total=float(row["total"]),
                bodega=row["bodega"],
                ubicacion=row["ubicacion"],
                referencia=f"COMPRA-{factura}",
                comentarios=comentarios
            )

        conn.commit()
        conn.close()

        st.session_state["detalle_compra_manual"] = []

        st.success(
            f"✅ Entrada registrada correctamente. Folio interno: {id_entrada}"
        )


if __name__ == "__main__":
    entrada_compras_app()
