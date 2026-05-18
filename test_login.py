import streamlit as st
import os
from pathlib import Path
import zipfile
from datetime import datetime

# Carpeta donde están las BD
BASE_DIR = Path("/mount/src/demonapp")

# Extensiones válidas
EXTENSIONES = [".db", ".sqlite", ".sqlite3"]


def obtener_bases():

    bases = []

    for archivo in BASE_DIR.iterdir():

        if archivo.is_file():

            if archivo.suffix.lower() in EXTENSIONES:

                bases.append(archivo)

    return bases


def crear_zip(lista_bases):

    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")

    nombre_zip = f"backup_sigem_{fecha}.zip"

    ruta_zip = BASE_DIR / nombre_zip

    with zipfile.ZipFile(
        ruta_zip,
        "w",
        zipfile.ZIP_DEFLATED
    ) as zipf:

        for bd in lista_bases:

            zipf.write(
                bd,
                arcname=bd.name
            )

    return ruta_zip


def descargar_todas_bd_app():

    st.title("⬇️ Respaldo Completo SIGEM")

    st.write("📂 Ruta configurada:")

    st.code(str(BASE_DIR))

    if not BASE_DIR.exists():

        st.error("❌ No existe la carpeta demonapp")

        st.stop()

    bases = obtener_bases()

    if len(bases) == 0:

        st.warning("⚠️ No se encontraron bases de datos")

        st.stop()

    st.success(f"✅ Se encontraron {len(bases)} BD")

    st.subheader("📦 Bases encontradas")

    for bd in bases:

        tamaño = os.path.getsize(bd)

        st.write(
            f"✅ {bd.name} — {tamaño:,} bytes"
        )

    st.divider()

    if st.button("📥 Generar respaldo ZIP"):

        try:

            ruta_zip = crear_zip(bases)

            st.success("✅ ZIP generado correctamente")

            with open(ruta_zip, "rb") as file:

                st.download_button(
                    label="⬇️ Descargar respaldo completo",
                    data=file,
                    file_name=ruta_zip.name,
                    mime="application/zip"
                )

        except Exception as e:

            st.error("❌ Error generando respaldo")

            st.exception(e)


descargar_todas_bd_app()
