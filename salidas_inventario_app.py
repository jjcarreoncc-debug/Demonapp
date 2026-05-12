import streamlit as st
import pandas as pd
import sqlite3
import re

from pathlib import Path
from datetime import datetime
from pypdf import PdfReader

from sigem_db import get_db_path
from inventario_db import crear_tabla_movimientos_inventario


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

    crear_tabla_movimientos_inventario()

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


def extraer_valor_por_etiqueta(texto_pdf, etiqueta):

    lineas = [
        linea.strip()
        for linea in texto_pdf.splitlines()
        if linea.strip()
    ]

    for i, linea in enumerate(lineas):

        if linea.lower() == etiqueta.lower():

            if i + 1 < len(lineas):
                return lineas[i + 1].strip()

    return ""


def extraer_datos_pdf(texto_pdf):

    datos = {
        "numero_documento": extraer_valor_por_etiqueta(texto_pdf, "Folio"),
        "codigo_material": extraer_valor_por_etiqueta(texto_pdf, "Material"),
        "cantidad": extraer_valor_por_etiqueta(texto_pdf, "Cantidad"),
        "bodega": extraer_valor_por_etiqueta(texto_pdf, "Bodega"),
        "ubicacion": extraer_valor_por_etiqueta(texto_pdf, "Ubicación"),
        "comentarios": extraer_valor_por_etiqueta(texto_pdf, "Comentarios"),
    }

    try:
        datos["cantidad"] = float(
            str(datos["cantidad"]).replace(",", ".")
        )

    except:
        datos["cantidad"] = 0.0

    return datos


def registrar_movimiento(
    folio_movimiento,
    tipo_movimiento,
    tipo_documento,
    numero_documento,
    archivo_documento,
    codigo_material,
    descripcion,
    cantidad,
    bodega,
    ubicacion,
    referencia,
    comentarios
):

    crear_tabla_movimientos_inventario()

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

        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        tipo_movimiento,

        tipo_documento,
        numero_documento,
        archivo_document
