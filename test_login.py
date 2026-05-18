import streamlit as st
import os


SEGURIDAD_DB_PATH = "/mount/src/demonapp/seguridad.db"


def descargar_seguridad_db_app():

    st.title("⬇️ Descargar seguridad.db")

    st.write("📂 Ruta configurada:")
    st.code(SEGURIDAD_DB_PATH)

    if not os.path.exists(SEGURIDAD_DB_PATH):

        st.error("❌ No existe seguridad.db")

        st.stop()

    tamaño = os.path.getsize(
        SEGURIDAD_DB_PATH
    )

    st.success("✅ seguridad.db encontrada")

    st.write(f"📦 Tamaño archivo: {tamaño} bytes")

    with open(
        SEGURIDAD_DB_PATH,
        "rb"
    ) as file:

        st.download_button(
            label="⬇️ Descargar seguridad.db",
            data=file,
            file_name="seguridad.db",
            mime="application/octet-stream"
        )


descargar_seguridad_db_app()
