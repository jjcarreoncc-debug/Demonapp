import streamlit as st
import os
import zipfile
from pathlib import Path
from datetime import datetime

st.title("💾 Backup completo SIGEM")

st.write("📂 Ruta fija configurada:")
st.code("/mount/src/demonapp")

# Validar ruta fija directamente
if not os.path.exists("/mount/src/demonapp"):
    st.error("❌ La ruta /mount/src/demonapp NO existe")
    st.stop()

if not os.path.isdir("/mount/src/demonapp"):
    st.error("❌ /mount/src/demonapp existe pero NO es una carpeta")
    st.stop()

st.success("✅ Ruta /mount/src/demonapp encontrada correctamente")

bases = []

# Buscar directo en la ruta fija
for archivo in Path("/mount/src/demonapp").rglob("*"):

    if archivo.is_file() and archivo.suffix.lower() in [".db", ".sqlite", ".sqlite3"]:

        tamaño = os.path.getsize(archivo)

        bases.append({
            "nombre": archivo.name,
            "ruta": str(archivo),
            "tamaño": tamaño
        })

if len(bases) == 0:
    st.error("❌ No se encontraron bases de datos en /mount/src/demonapp")
    st.stop()

st.success(f"✅ Se encontraron {len(bases)} archivo(s) de base de datos")

st.subheader("📦 Bases encontradas")

bases_validas = []

for bd in bases:

    st.write(f"📄 **{bd['nombre']}**")
    st.write("📍 Ruta exacta:")
    st.code(bd["ruta"])
    st.write(f"📏 Tamaño: {bd['tamaño']:,} bytes")

    if bd["tamaño"] == 0:
        st.warning("⚠️ Esta BD está vacía y NO se incluirá en el backup")
    else:
        st.success("✅ Esta BD sí se incluirá en el backup")
        bases_validas.append(bd)

    st.divider()

if len(bases_validas) == 0:
    st.error("❌ No hay bases con datos para respaldar")
    st.stop()

if st.button("📥 Generar Backup ZIP"):

    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")

    nombre_zip = f"SIGEM_BACKUP_{fecha}.zip"

    ruta_zip = f"/mount/src/demonapp/{nombre_zip}"

    try:

        with zipfile.ZipFile(
            ruta_zip,
            "w",
            zipfile.ZIP_DEFLATED
        ) as zipf:

            for bd in bases_validas:

                zipf.write(
                    bd["ruta"],
                    arcname=bd["nombre"]
                )

        st.success("✅ Backup generado correctamente")

        st.write("📦 Archivo ZIP creado en:")
        st.code(ruta_zip)

        with open(ruta_zip, "rb") as file:

            st.download_button(
                label="⬇️ Descargar Backup a mi PC",
                data=file,
                file_name=nombre_zip,
                mime="application/zip"
            )

    except Exception as e:

        st.error("❌ Error generando backup")
        st.exception(e)
