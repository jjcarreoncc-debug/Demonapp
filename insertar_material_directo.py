import streamlit as st
from datetime import datetime

from sigem_db import get_db_path, get_materiales_connection


st.title("🧪 Insert debug materiales")

st.markdown("## 1️⃣ Ruta oficial desde SIGEM")

DB_PATH = get_db_path("materiales")

st.write("📂 Ruta que devuelve sigem_db.py:")
st.code(str(DB_PATH))

st.write("📦 Existe archivo DB:")
st.write(DB_PATH.exists())

if DB_PATH.exists():
    st.write("📏 Tamaño bytes:")
    st.write(DB_PATH.stat().st_size)


material = {
    "codigo_material": "MAT-001",
    "descripcion": "Laptop Dell Latitude",
    "categoria": "Tecnología",
    "familia": "Computo",
    "unidad_base": "PZA",
    "estatus": "Activo"
}


st.markdown("## 2️⃣ Material que se quiere insertar")
st.json(material)


if st.button("🚀 Probar insert MAT-001"):

    st.markdown("## 3️⃣ Abriendo conexión")

    try:
        conn = get_materiales_connection()
        cur = conn.cursor()

        st.success("✅ Conexión abierta con get_materiales_connection()")

        st.markdown("## 4️⃣ Tablas existentes ANTES del insert")

        tablas = cur.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            ORDER BY name
        """).fetchall()

        tablas_lista = [t[0] for t in tablas]

        st.write(tablas_lista)

        if "materiales" not in tablas_lista:
            st.error("❌ La tabla materiales NO existe en esta conexión.")
            conn.close()
            st.stop()

        st.success("✅ La tabla materiales sí existe")

        st.markdown("## 5️⃣ Ejecutando INSERT")

        cur.execute("""
            INSERT OR REPLACE INTO materiales (
                codigo_material,
                descripcion,
                categoria,
                familia,
                unidad_base,
                estatus,
                fecha_creacion,
                usuario_creacion
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            material["codigo_material"],
            material["descripcion"],
            material["categoria"],
            material["familia"],
            material["unidad_base"],
            material["estatus"],
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "admin"
        ))

        st.success("✅ INSERT ejecutado")

        st.markdown("## 6️⃣ Commit")

        conn.commit()

        st.success("✅ Commit realizado")

        st.markdown("## 7️⃣ Validando registros")

        total = cur.execute("""
            SELECT COUNT(*)
            FROM materiales
        """).fetchone()[0]

        st.write("📊 Total registros en materiales:")
        st.write(total)

        df = cur.execute("""
            SELECT *
            FROM materiales
            ORDER BY codigo_material
        """).fetchall()

        columnas = [desc[0] for desc in cur.description]

        st.write("📋 Columnas:")
        st.write(columnas)

        st.write("📦 Registros:")
        st.write([dict(zip(columnas, row)) for row in df])

        conn.close()

        st.success("✅ Proceso terminado correctamente")

    except Exception as e:
        st.error("❌ Error en proceso de insert")
        st.exception(e)
