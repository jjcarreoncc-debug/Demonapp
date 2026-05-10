import streamlit as st
import sqlite3
import pandas as pd


DB_NAME = "materiales.db"


def crear_tabla_materiales():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS materiales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_material TEXT UNIQUE,
            descripcion TEXT,
            descripcion_larga TEXT,
            categoria TEXT,
            familia TEXT,
            marca TEXT,
            tipo_material TEXT,
            estatus TEXT,
            unidad_base TEXT,
            controla_lote INTEGER,
            controla_serie INTEGER,
            peso REAL,
            volumen REAL,
            largo REAL,
            ancho REAL,
            alto REAL,
            tipo_almacenamiento TEXT,
            almacen_default TEXT,
            ubicacion_default TEXT,
            rotacion_abc TEXT,
            costo_estandar REAL,
            precio_compra REAL,
            precio_venta REAL,
            moneda TEXT,
            impuesto TEXT,
            margen_objetivo REAL,
            stock_minimo REAL,
            stock_maximo REAL,
            punto_reorden REAL,
            lead_time INTEGER,
            permite_negativo INTEGER,
            requiere_inspeccion INTEGER,
            codigo_barras TEXT,
            sku_base TEXT,
            codigo_sap TEXT,
            proveedor_principal TEXT,
            usuario_creacion TEXT
        )
    """)

    conn.commit()
    conn.close()


def insertar_material(data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    columnas = ", ".join(data.keys())
    signos = ", ".join(["?"] * len(data))
    valores = list(data.values())

    cursor.execute(
        f"""
        INSERT OR IGNORE INTO materiales ({columnas})
        VALUES ({signos})
        """,
        valores
    )

    conn.commit()
    conn.close()


def cargar_materiales_demo():
    materiales = [
        ("MAT-001", "Tornillo 1/4", "Refacción", "Ferretería", "PZA", "Activo"),
        ("MAT-002", "Caja cartón chica", "Empaque", "Cartón", "PZA", "Activo"),
        ("MAT-003", "Aceite industrial", "Materia prima", "Químicos", "LT", "Activo"),
        ("MAT-004", "Etiqueta térmica", "Empaque", "Etiquetas", "PZA", "Activo"),
        ("MAT-005", "Bolsa polietileno", "Empaque", "Plásticos", "PZA", "Activo"),
        ("MAT-006", "Motor eléctrico", "Refacción", "Eléctrico", "PZA", "Activo"),
        ("MAT-007", "Cable calibre 12", "Refacción", "Eléctrico", "MT", "Activo"),
        ("MAT-008", "Pintura blanca", "Materia prima", "Pinturas", "LT", "Activo"),
        ("MAT-009", "Tarima madera", "Empaque", "Tarimas", "PZA", "Activo"),
        ("MAT-010", "Sensor óptico", "Refacción", "Sensores", "PZA", "Activo"),
        ("MAT-011", "Cinta adhesiva", "Empaque", "Consumibles", "PZA", "Activo"),
        ("MAT-012", "Guante nitrilo", "Insumo", "Seguridad", "PZA", "Activo"),
        ("MAT-013", "Lubricante grado alimenticio", "Materia prima", "Lubricantes", "LT", "Activo"),
        ("MAT-014", "Filtro aire", "Refacción", "Filtros", "PZA", "Activo"),
        ("MAT-015", "Servicio mantenimiento", "Servicio", "Servicios", "SERV", "Activo"),
    ]

    for codigo, descripcion, categoria, familia, unidad, estatus in materiales:
        data = {
            "codigo_material": codigo,
            "descripcion": descripcion,
            "descripcion_larga": descripcion,
            "categoria": categoria,
            "familia": familia,
            "marca": "Genérico",
            "tipo_material": "Almacenable" if categoria != "Servicio" else "Servicio",
            "estatus": estatus,
            "unidad_base": unidad,
            "controla_lote": 0,
            "controla_serie": 0,
            "peso": 0.0,
            "volumen": 0.0,
            "largo": 0.0,
            "ancho": 0.0,
            "alto": 0.0,
            "tipo_almacenamiento": "General",
            "almacen_default": "CEDI",
            "ubicacion_default": "GEN-001",
            "rotacion_abc": "B",
            "costo_estandar": 10.0,
            "precio_compra": 12.0,
            "precio_venta": 18.0,
            "moneda": "MXN",
            "impuesto": "IVA 16%",
            "margen_objetivo": 30.0,
            "stock_minimo": 10.0,
            "stock_maximo": 100.0,
            "punto_reorden": 25.0,
            "lead_time": 5,
            "permite_negativo": 0,
            "requiere_inspeccion": 0,
            "codigo_barras": "",
            "sku_base": codigo,
            "codigo_sap": "",
            "proveedor_principal": "Proveedor demo",
            "usuario_creacion": "admin"
        }

        insertar_material(data)


def tabla_existe():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name='materiales'
    """)

    existe = cursor.fetchone() is not None

    conn.close()

    return existe


def mostrar_materiales():
    if not tabla_existe():
        st.warning("La tabla materiales todavía no existe.")
        return

    conn = sqlite3.connect(DB_NAME)

    df = pd.read_sql_query("SELECT * FROM materiales", conn)

    conn.close()

    st.subheader("📋 Registros actuales")
    st.success(f"Total registros: {len(df)}")
    st.dataframe(df, use_container_width=True)


def app():
    st.title("🧪 Crear y cargar tabla materiales")

    if st.button("Crear tabla e insertar materiales demo"):
        crear_tabla_materiales()
        cargar_materiales_demo()
        st.success("✅ Tabla creada y materiales insertados")

    st.markdown("---")

    mostrar_materiales()


if __name__ == "__main__":
    app()
