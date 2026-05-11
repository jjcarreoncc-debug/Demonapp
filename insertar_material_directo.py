import streamlit as st
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "materiales.db"

st.title("🚀 Insertar material directo simple")
st.code(str(DB_PATH))

if st.button("Insertar MAT-001"):

    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        cur.execute("""
            INSERT OR REPLACE INTO materiales (
                codigo_material,
                descripcion,
                categoria,
                familia,
                unidad_base,
                estatus
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "MAT-001",
            "Laptop Dell Latitude",
            "Tecnología",
            "Computo",
            "PZA",
            "Activo"
        ))

        conn.commit()

        total = cur.execute(
            "SELECT COUNT(*) FROM materiales"
        ).fetchone()[0]

        conn.close()

        st.success(f"✅ Insertado. Total registros: {total}")

    except Exception as e:
        st.error("❌ Error insertando")
        st.exception(e)
