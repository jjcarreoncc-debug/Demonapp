import streamlit as st
import sqlite3
import random
from datetime import datetime, timedelta

from sigem_db import get_db_path


def carga_demo_analitica_inventarios_app():

    st.title("📊 Carga Demo Analítica Inventarios")
    st.caption("Genera movimientos demo para alimentar dashboards analíticos.")

    if st.button("🚀 Generar datos demo", use_container_width=True):

        conn = sqlite3.connect(get_db_path("inventarios"))
        cur = conn.cursor()

        try:

            # =========================
            # OBTENER MATERIALES
            # =========================
            cur.execute("""
                ATTACH DATABASE ? AS materiales_db
            """, (get_db_path("materiales"),))

            cur.execute("""
                SELECT
                    codigo_material,
                    descripcion
                FROM materiales_db.materiales
                WHERE estatus = 'Activo'
            """)

            materiales = cur.fetchall()

            if not materiales:
                st.warning("No existen materiales activos.")
                conn.close()
                return

            # =========================
            # LIMPIAR DEMO ANTERIOR
            # =========================
            cur.execute("""
                DELETE FROM movimientos_inventario
                WHERE referencia = 'DEMO_ANALITICA'
            """)

            # =========================
            # GENERAR MOVIMIENTOS
            # =========================
            tipos = [
                "ENTRADA_COMPRA",
                "SALIDA_VENTA",
                "ENTRADA_AJUSTE",
                "SALIDA_AJUSTE"
            ]

            bodegas = ["CENTRAL", "NORTE", "SUR"]
            ubicaciones = ["A-01", "B-01", "C-01"]

            total_movs = 0

            for material in materiales:

                codigo = material[0]
                descripcion = material[1]

                movimientos_material = random.randint(10, 40)

                for i in range(movimientos_material):

                    tipo = random.choice(tipos)

                    if "ENTRADA" in tipo:
                        cantidad = random.randint(5, 50)
                    else:
                        cantidad = random.randint(1, 25) * -1

                    fecha = (
                        datetime.now()
                        - timedelta(days=random.randint(1, 180))
                    ).strftime("%Y-%m-%d %H:%M:%S")

                    folio = f"DEMO-{datetime.now().strftime('%Y%m%d%H%M%S')}-{i}"

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
                        f"DOC-{i}",
                        "",
                        codigo,
                        descripcion,
                        cantidad,
                        random.randint(10, 500),
                        0,
                        random.choice(bodegas),
                        random.choice(ubicaciones),
                        "DEMO_ANALITICA",
                        "Carga demo analítica inventarios",
                        "admin"
                    ))

                    total_movs += 1

            conn.commit()

            st.success(
                f"✅ Datos demo generados correctamente. "
                f"Movimientos creados: {total_movs}"
            )

        except Exception as e:

            st.error("❌ Error generando demo.")
            st.exception(e)

        finally:
            conn.close()
