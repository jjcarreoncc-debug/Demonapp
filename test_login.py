import streamlit as st
import os


def buscar_bases():

    st.title("🔎 Buscar bases de datos")

    st.subheader("📂 Archivos encontrados en el proyecto")

    try:

        archivos = os.listdir(".")

        st.write(archivos)

        st.markdown("---")

        st.subheader("🗄️ Bases de datos encontradas")

        dbs = [
            a for a in archivos
            if a.endswith(".db")
            or a.endswith(".sqlite")
            or a.endswith(".sqlite3")
        ]

        if dbs:

            st.success(f"Se encontraron {len(dbs)} bases")

            for db in dbs:
                st.write("✅", db)

        else:

            st.warning("❌ No encontré bases de datos")

    except Exception as e:

        st.error("❌ Error al buscar archivos")
        st.exception(e)


if __name__ == "__main__":
    buscar_bases()
