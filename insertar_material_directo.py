import streamlit as st
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent / "materiales.db"

st.title("🚀 Insertar material directo")
st.code(str(DB_PATH))

if st.button("Insertar MAT-001"):

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        INSERT OR REPLACE INTO materiales (
            codigo_material,
            descripcion,
            descripcion_larga,
            categoria,
            familia,
            marca,
            tipo_material,
            estatus,
            unidad_base,
            controla_lote,
            controla_serie,
            peso,
            volumen,
            largo,
            ancho,
            alto,
            tipo_almacenamiento,
            almacen_default,
            ubicacion_default,
            rotacion_abc,
            costo_estandar,
            precio_compra,
            precio_venta,
            moneda,
            impuesto,
            margen_objetivo,
            stock_minimo,
            stock_maximo,
            punto_reorden,
            lead_time,
            permite_negativo,
            requiere_inspeccion,
            codigo_barras,
            sku_base,
            codigo_sap,
            proveedor_principal,
            fecha_creacion,
            usuario_creacion
        )
        VALUES (
            'MAT-001',
            'Laptop Dell Latitude',
            'Laptop corporativa Dell Latitude',
            'Tecnología',
            'Computo',
            'Dell',
            'Producto',
            'Activo',
            'PZA',
            0,
            1,
            2.5,
            0.02,
            35,
            24,
            3,
            'Rack',
            'ALM-TEC',
            'A1',
            'A',
            18000,
            17500,
            22000,
            'MXN',
            'IVA',
            20,
            5,
            50,
            10,
            7,
            0,
            1,
            '750000000001',
            'SKU-001',
            'SAP-001',
            'Dell México',
            ?,
            'admin'
        )
    """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),))

    conn.commit()

    total = cur.execute("SELECT COUNT(*) FROM materiales").fetchone()[0]

    conn.close()

    st.success(f"✅ Insertado. Total registros: {total}")
