import sqlite3
import random
from datetime import datetime, timedelta

from sigem_db import get_db_path


def main():
    conn = sqlite3.connect(get_db_path("inventarios"))
    cur = conn.cursor()

    cur.execute(
        f"ATTACH DATABASE '{get_db_path('materiales')}' AS materiales_db"
    )

    cur.execute("""
        SELECT codigo_material, descripcion
        FROM materiales_db.materiales
       
    """)

    materiales = cur.fetchall()

    if not materiales:
        print("No hay materiales activos.")
        conn.close()
        return

    cur.execute("""
        DELETE FROM movimientos_inventario
        WHERE referencia = 'DEMO_ANALITICA'
    """)

    tipos = [
        "ENTRADA_COMPRA",
        "SALIDA_VENTA",
        "ENTRADA_AJUSTE",
        "SALIDA_AJUSTE"
    ]

    bodegas = ["CENTRAL", "NORTE", "SUR"]
    ubicaciones = ["A-01", "B-01", "C-01", "D-01"]

    total = 0

    for codigo, descripcion in materiales:
        for i in range(random.randint(80, 150)):
            tipo = random.choice(tipos)

            if "ENTRADA" in tipo:
                cantidad = random.randint(10, 80)
            else:
                cantidad = random.randint(1, 45) * -1

            fecha = (
                datetime.now() - timedelta(days=random.randint(1, 180))
            ).strftime("%Y-%m-%d %H:%M:%S")

            costo = random.randint(20, 600)

            folio = f"DEMO-{codigo}-{i}-{datetime.now().strftime('%H%M%S')}"

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
                folio,
                fecha,
                tipo,
                "DEMO",
                f"DOC-{total}",
                "",
                codigo,
                descripcion,
                cantidad,
                costo,
                cantidad * costo,
                random.choice(bodegas),
                random.choice(ubicaciones),
                "DEMO_ANALITICA",
                "Carga demo batch analítica inventarios",
                "admin"
            ))

            total += 1

    conn.commit()
    conn.close()

    print(f"✅ Carga demo terminada. Movimientos creados: {total}")


if __name__ == "__main__":
    main()
