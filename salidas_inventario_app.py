import streamlit as st
import pandas as pd
import sqlite3
import re

from pathlib import Path
from datetime import datetime
from pypdf import PdfReader

from sigem_db import get_db_path


def obtener_materiales():

    db_path = get_db_path("materiales")
    conn = sqlite3.connect(db_path)

    try:
        query = """
            SELECT
                codigo_material,
                descripcion
            FROM materiales
            ORDER BY codigo_material
        """

        df = pd.read_sql(query, conn)

    except Exception as e:
        st.error("Error leyendo materiales.db")
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


def generar_folio():

    fecha = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"SG201-{fecha}"


def leer_pdf(archivo_pdf):

    texto_pdf = ""

    try:
        reader = PdfReader(archivo_pdf)

        for page in reader.pages:
            texto_pdf += page.extract_text() or ""

    except Exception as e:
        st.error("Error leyendo PDF")
        st.exception(e)

    return texto_pdf


def extraer_numero_documento(texto_pdf):

    patrones = [
        r"Folio[:\s]+([A-Z0-9\-]+)",
        r"Documento[:\s]+([A-Z0-9\-]+)",
        r"Remisión[:\s]+([A-Z0-9\-]+)",
        r"Venta[:\s]+([A-Z0-9\-]+)",
        r"Vale[:\s]+([A-Z0-9\-]+)"
    ]

    for patron in patrones:
        encontrado = re.search(patron, texto_pdf, re.IGNORECASE)
        if encontrado:
            return encontrado.group(1)

    return ""


def registrar_movimiento(
    folio_movimiento,
    tipo_movimiento,
    tipo_documento,
    numero_documento,
    archivo_documento,
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
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        tipo_movimiento,
        tipo_documento,
        numero_documento,
        archivo_documento,
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
        st.warning("No existen materiales registrados.")
        return

    st.subheader("🧾 Documento salida")

    c1, c2 = st.columns(2)

    with c1:
        tipo_documento = st.selectbox(
            "Tipo documento",
            [
                "VENTA",
                "REMISION",
                "VALE_SALIDA",
                "ORDEN_INTERNA",
                "MERMA",
                "TRANSFERENCIA",
                "AJUSTE_AUTORIZADO"
            ]
        )

    with c2:
        numero_documento = st.text_input("Número documento")

    archivo = st.file_uploader(
        "Adjuntar PDF obligatorio",
        type=["pdf"],
        key="archivo_pdf_salida"
    )

    st.markdown("---")
    st.subheader("📄 Lectura del PDF")

    texto_pdf = ""

    if archivo is not None:

        st.success(f"PDF adjuntado: {archivo.name}")

        leer_pdf_btn = st.button(
            "🔍 Leer PDF",
            key="btn_leer_pdf_salida"
        )

        if leer_pdf_btn:

            texto_pdf = leer_pdf(archivo)

            if texto_pdf.strip():

                st.success("✅ Texto detectado en el PDF")

                st.text_area(
                    "Texto leído del PDF",
                    texto_pdf,
                    height=250
                )

                numero_detectado = extraer_numero_documento(texto_pdf)

                if numero_detectado:
                    st.info(f"Número documento detectado: {numero_detectado}")
                else:
                    st.warning("No se detectó número de documento en el PDF.")

            else:
                st.warning(
                    "No se detectó texto. Puede ser un PDF escaneado y necesitar OCR."
                )

    else:
        st.info("Adjunta un PDF para habilitar la lectura.")

    st.subheader("📝 Información salida")

    referencia = st.text_input("Referencia")

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

        if not numero_documento:
            st.error("Debes capturar número documento.")
            return

        if archivo is None:
            st.error("Debes adjuntar PDF obligatorio.")
            return

        if cantidad <= 0:
            st.error("Cantidad inválida.")
            return

        if cantidad > existencia:
            st.error("No existe stock suficiente.")
            return

        carpeta = (
            Path(__file__).resolve().parent
            / "documentos"
            / "salidas"
        )

        carpeta.mkdir(
            parents=True,
            exist_ok=True
        )

        ruta_archivo = carpeta / archivo.name

        with open(ruta_archivo, "wb") as f:
            f.write(archivo.getbuffer())

        folio_movimiento = generar_folio()

        registrar_movimiento(
            folio_movimiento,
            "SALIDA",
            tipo_documento,
            numero_documento,
            str(ruta_archivo),
            codigo_material,
            descripcion,
            cantidad * -1,
            referencia,
            comentarios
        )

        st.success("✅ Salida registrada correctamente")

        st.subheader("📄 Confirmación movimiento")

        st.success(f"Folio movimiento: {folio_movimiento}")

        st.write("Tipo documento:", tipo_documento)
        st.write("Número documento:", numero_documento)
        st.write("Material:", codigo_material)
        st.write("Descripción:", descripcion)
        st.write("Cantidad salida:", cantidad)
        st.write("Archivo:", archivo.name)


if __name__ == "__main__":
    salidas_inventario_app()
