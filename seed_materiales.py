from materiales_db import insertar_material


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
        "controla_lote": False,
        "controla_serie": False,
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
        "permite_negativo": False,
        "requiere_inspeccion": False,
        "codigo_barras": "",
        "sku_base": codigo,
        "codigo_sap": "",
        "proveedor_principal": "Proveedor demo",
        "usuario_creacion": "admin"
    }

    try:
        insertar_material(data)
        print(f"✅ Insertado: {codigo}")
    except Exception as e:
        print(f"⚠️ No insertado {codigo}: {e}")


print("✅ Seed terminado")
