```python
from materiales_db import insertar_material


materiales_demo = [

    {
        "codigo_material": "MAT-001",
        "descripcion": "Laptop Dell Latitude",
        "descripcion_larga": "Laptop corporativa Dell Latitude 14 pulgadas",
        "categoria": "Tecnología",
        "familia": "Computo",
        "marca": "Dell",
        "tipo_material": "Producto",
        "estatus": "Activo",
        "unidad_base": "PZA",
        "controla_lote": False,
        "controla_serie": True,
        "peso": 2.5,
        "volumen": 0.02,
        "largo": 35,
        "ancho": 24,
        "alto": 3,
        "tipo_almacenamiento": "Rack",
        "almacen_default": "ALM-TEC",
        "ubicacion_default": "A1",
        "rotacion_abc": "A",
        "costo_estandar": 18000,
        "precio_compra": 17500,
        "precio_venta": 22000,
        "moneda": "MXN",
        "impuesto": "IVA",
        "margen_objetivo": 20,
        "stock_minimo": 5,
        "stock_maximo": 50,
        "punto_reorden": 10,
        "lead_time": 7,
        "permite_negativo": False,
        "requiere_inspeccion": True,
        "codigo_barras": "750000000001",
        "sku_base": "SKU-001",
        "codigo_sap": "SAP-001",
        "proveedor_principal": "Dell México"
    },

    {
        "codigo_material": "MAT-002",
        "descripcion": "Mouse Logitech",
        "descripcion_larga": "Mouse inalámbrico Logitech",
        "categoria": "Tecnología",
        "familia": "Accesorios",
        "marca": "Logitech",
        "tipo_material": "Producto",
        "estatus": "Activo",
        "unidad_base": "PZA",
        "controla_lote": False,
        "controla_serie": False,
        "peso": 0.2,
        "volumen": 0.01,
        "largo": 12,
        "ancho": 6,
        "alto": 4,
        "tipo_almacenamiento": "Rack",
        "almacen_default": "ALM-TEC",
        "ubicacion_default": "A2",
        "rotacion_abc": "B",
        "costo_estandar": 250,
        "precio_compra": 200,
        "precio_venta": 350,
        "moneda": "MXN",
        "impuesto": "IVA",
        "margen_objetivo": 30,
        "stock_minimo": 20,
        "stock_maximo": 200,
        "punto_reorden": 40,
        "lead_time": 3,
        "permite_negativo": False,
        "requiere_inspeccion": False,
        "codigo_barras": "750000000002",
        "sku_base": "SKU-002",
        "codigo_sap": "SAP-002",
        "proveedor_principal": "Logitech"
    },

    {
        "codigo_material": "MAT-003",
        "descripcion": "Teclado HP",
        "descripcion_larga": "Teclado USB HP",
        "categoria": "Tecnología",
        "familia": "Accesorios",
        "marca": "HP",
        "tipo_material": "Producto",
        "estatus": "Activo",
        "unidad_base": "PZA",
        "controla_lote": False,
        "controla_serie": False,
        "peso": 0.6,
        "volumen": 0.01,
        "largo": 45,
        "ancho": 15,
        "alto": 4,
        "tipo_almacenamiento": "Rack",
        "almacen_default": "ALM-TEC",
        "ubicacion_default": "A3",
        "rotacion_abc": "B",
        "costo_estandar": 400,
        "precio_compra": 350,
        "precio_venta": 550,
        "moneda": "MXN",
        "impuesto": "IVA",
        "margen_objetivo": 25,
        "stock_minimo": 15,
        "stock_maximo": 100,
        "punto_reorden": 25,
        "lead_time": 5,
        "permite_negativo": False,
        "requiere_inspeccion": False,
        "codigo_barras": "750000000003",
        "sku_base": "SKU-003",
        "codigo_sap": "SAP-003",
        "proveedor_principal": "HP"
    }
]


# =========================
# DUPLICAR HASTA 10
# =========================
for i in range(4, 11):

    nuevo = materiales_demo[1].copy()

    nuevo["codigo_material"] = f"MAT-{i:03}"
    nuevo["descripcion"] = f"Material Demo {i}"
    nuevo["sku_base"] = f"SKU-{i:03}"
    nuevo["codigo_sap"] = f"SAP-{i:03}"
    nuevo["codigo_barras"] = f"7500000000{i:02}"

    materiales_demo.append(nuevo)


# =========================
# INSERTAR
# =========================
for material in materiales_demo:

    try:

        insertar_material(material)
        print(f"OK -> {material['codigo_material']}")

    except Exception as e:

        print(f"ERROR -> {material['codigo_material']} -> {e}")


print("Carga finalizada")
```

Guárdalo como:

```text
cargar_materiales_demo.py
```

Y ejecútalo con:

```bash
python cargar_materiales_demo.py
```
