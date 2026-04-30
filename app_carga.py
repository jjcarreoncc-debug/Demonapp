import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

st.set_page_config(page_title="Carga de Datos", layout="wide")

st.title("📂 Carga de Excel a Base de Datos")

# -------------------------
# CONFIGURACIÓN
# -------------------------
DB_NAME = "data.db"

# -------------------------
# SUBIR ARCHIVO
# -------------------------
archivo = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if archivo:

    df = pd.read_excel(archivo)
    df.columns = df.columns.str.strip()

    st.subheader("👀 Vista previa")
    st.dataframe(df.head())

    st.markdown("---")

    # -------------------------
    # VALIDACIONES BÁSICAS
    # -------------------------
    st.subheader("🔎 Validaciones")

    columnas_requeridas = ["Fecha"]

    faltantes = [c for c in columnas_requeridas if c not in df.columns]

    if faltantes:
        st.error(f"Faltan columnas obligatorias: {faltantes}")
        st.stop()
    else:
        st.success("Columnas obligatorias OK")

    # Validar fecha
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")

    if df["Fecha"].isna().sum() > 0:
        st.warning("Algunas fechas no son válidas y serán ignoradas")

    # -------------------------
    # CONFIGURACIÓN DE CARGA
    # -------------------------
    st.subheader("⚙️ Configuración")

    nombre_tabla = st.text_input("Nombre de la tabla", value="ventas")

    modo = st.radio(
        "Modo de carga",
        ["Reemplazar tabla", "Agregar registros"]
    )

    # -------------------------
    # BOTÓN GUARDAR
    # -------------------------
    if st.button("💾 Guardar en base de datos"):

        try:
            conn = sqlite3.connect(DB_NAME)

            if modo == "Reemplazar tabla":
                df.to_sql(nombre_tabla, conn, if_exists="replace", index=False)

            else:
                df.to_sql(nombre_tabla, conn, if_exists="append", index=False)

            conn.close()

            st.success("Datos guardados correctamente")

            # -------------------------
            # RESUMEN
            # -------------------------
            st.subheader("📊 Resumen de carga")

            st.write(f"Filas cargadas: {len(df)}")
            st.write(f"Columnas: {len(df.columns)}")
            st.write(f"Tabla: {nombre_tabla}")
            st.write(f"Fecha carga: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        except Exception as e:
            st.error(f"Error al guardar: {e}")

else:
    st.info("📂 Sube un archivo para comenzar")
```
