import streamlit as st
import pandas as pd
import sqlite3

from sigem_db import get_db_path


def obtener_estructura(conn):

    return pd.read_sql_query(
        "PRAGMA table_info(movimientos_inventario)",
        conn
    )


def actualizar_movimientos_inventario_app():

    st.title("🛠️ Actualizar estructura movimientos_inventario")

    db_path = get_db_path("inventarios")

    st.subheader("📂 Base utilizada")
    st.code(str(db_path))

    columnas_requeridas = [
        ("folio_movimiento", "TEXT"),
        ("tipo_documento", "TEXT"),
        ("numero_documento", "TEXT"),
        ("archivo_documento", "TEXT"),
        ("referencia", "TEXT"),
        ("comentarios", "TEXT"),
        ("usuario", "TEXT"),
    ]

    try:

        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        st.subheader("📋 Estructura actual")

        df_actual = obtener_estructura(conn)

        if df_actual.empty:
            st.error("❌ La tabla movimientos_inventario no existe.")
            conn.close()
            return

        st.dataframe(df_actual, use_container_width=True)

        columnas_actuales = df_actual["name"].tolist()

        st.subheader("🔎 Validación columnas requeridas")

        faltantes = []

        for columna, tipo in columnas_requeridas:

            if columna in columnas_actuales:
                st.success(f"✅ Existe: {columna}")
            else:
                st.error(f"❌ Falta: {columna}")
                faltantes.append((columna, tipo))

        if not faltantes:
            st.success("✅ La tabla ya tiene toda la estructura requerida.")

        st.markdown("---")

        if st.button("🚀 Actualizar estructura"):

            if not faltantes:
                st.info("No hay columnas faltantes para agregar.")
            else:

                for columna, tipo in faltantes:

                    try:
                        cur.execute(
                            f"""
                            ALTER TABLE movimientos_inventario
                            ADD COLUMN {columna} {tipo}
                            """
                        )

                        st.success(f"Columna agregada: {columna}")

                    except sqlite3.OperationalError as e:
                        st.warning(f"No se pudo agregar {columna}: {e}")

                conn.commit()

                st.success("✅ Actualización terminada.")

            st.subheader("📋 Estructura final")

            df_final = obtener_estructura(conn)

            st.dataframe(df_final, use_container_width=True)

        conn.close()

    except Exception as e:

        st.error("Error actualizando movimientos_inventario")
        st.exception(e)


if __name__ == "__main__":
    actualizar_movimientos_inventario_app()
