import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
from datetime import datetime

from sigem_db import get_db_path


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


def entrada_compras_app():

    st.title("📥 Entrada de Compras / Factura")

    crear_tablas_entrada_compras()

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

    st.subheader("📎 Documento digitalizado")

    archivo = st.file_uploader(
        "Adjuntar factura PDF / imagen / Excel",
        type=["pdf", "png", "jpg", "jpeg", "xlsx"]
    )

    archivo_guardado = ""

    if archivo is not None:
        carpeta = Path(__file__).resolve().parent / "documentos" / "compras"
        carpeta.mkdir(parents=True, exist_ok=True)

        archivo_guardado = carpeta / archivo.name

        with open(archivo_guardado, "wb") as f:
            f.write(archivo.getbuffer())

        st.success(f"Archivo adjuntado: {archivo.name}")

    st.subheader("📦 Detalle materiales")

    detalle_base = pd.DataFrame([
        {
            "codigo_material": "",
            "descripcion": "",
            "cantidad": 0.0,
            "costo_unitario": 0.0,
            "impuesto": 0.0,
            "bodega": "",
            "ubicacion": ""
        }
    ])

    detalle = st.data_editor(
        detalle_base,
        num_rows="dynamic",
        use_container_width=True,
        key="detalle_entrada_compras"
    )

    if not detalle.empty:
        detalle["total"] = (
            detalle["cantidad"].fillna(0)
            * detalle["costo_unitario"].fillna(0)
        ) + detalle["impuesto"].fillna(0)

        st.write("Vista previa total:")
        st.dataframe(detalle, use_container_width=True)

    if st.button("💾 Registrar entrada de compras"):

        if not proveedor or not factura:
            st.error("Proveedor y factura son obligatorios.")
            return

        detalle_valido = detalle[
            (detalle["codigo_material"].astype(str).str.strip() != "")
            & (detalle["cantidad"] > 0)
        ]

        if detalle_valido.empty:
            st.error("Debes capturar al menos un material con cantidad mayor a cero.")
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
            str(archivo_guardado),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            st.session_state.get("usuario", "admin")
        ))

        id_entrada = cur.lastrowid

        for _, row in detalle_valido.iterrows():

            total = (
                float(row["cantidad"])
                * float(row["costo_unitario"])
            ) + float(row["impuesto"])

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
                total,
                row["bodega"],
                row["ubicacion"]
            ))

        conn.commit()
        conn.close()

        st.success(f"✅ Entrada registrada correctamente. Folio interno: {id_entrada}")


if __name__ == "__main__":
    entrada_compras_app()
