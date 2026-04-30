import streamlit as st
import pandas as pd
import sqlite3
import os

st.set_page_config(page_title="Carga de Datos", layout="wide")

st.title("📂 Carga de datos a base")

# =========================
# CONFIG
# =========================
DB_NAME = "data.db"

st.write("RUTA CARGA:", os.getcwd())

# =========================
# SUBIR ARCHIVO
# =========================
archivo = st.file_uploader("📂 Sube tu archivo Excel", type=["xlsx"])

if archivo:

    with st.spinner("Procesando archivo..."):
        try:
            df = pd.read_excel(archivo)
        except Exception as e:
            st.error(f"Error leyendo archivo: {e}")
            st.stop()

    st.success("Archivo cargado correctamente")
    st.write("Filas:", len(df))

    # =========================
    # LIMPIEZA
    # =========================
    df.columns = df.columns.str.strip()

    # Validación columnas clave
    columnas_minimas = ["Fecha", "Ventas_Cantidad"]

    faltantes = [c for c in columnas_minimas if c not in df.columns]

    if faltantes:
        st.error(f"Faltan columnas obligatorias: {faltantes}")
        st.stop()
    else:
        st.success("Columnas obligatorias OK")

    # Fecha
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    invalidas = df["Fecha"].isna().sum()

    if invalidas > 0:
        st.warning("Algunas fechas no son válidas y serán ignoradas")

    df = df.dropna(subset=["Fecha"])

    # =========================
    # CONFIGURACIÓN
    # =========================
    st.subheader("⚙️ Configuración")

    nombre_tabla = st.text_input("Nombre de la tabla", value="ventas")

    modo = st.selectbox(
        "Modo de carga",
        ["Reemplazar tabla", "Agregar (evitar duplicados)"]
    )

    # =========================
    # GUARDAR
    # =========================
    if st.button("💾 Guardar en base de datos"):

        try:
            conn = sqlite3.connect(DB_NAME)

            if modo == "Reemplazar tabla":
                df.to_sql(nombre_tabla, conn, if_exists="replace", index=False)

            else:
                # evitar duplicados
                try:
                    df_db = pd.read_sql(f"SELECT * FROM {nombre_tabla}", conn)
                    df_final = pd.concat([df_db, df]).drop_duplicates()
                except:
                    df_final = df

                df_final.to_sql(nombre_tabla, conn, if_exists="replace", index=False)

            conn.commit()
            conn.close()

            st.success("Datos guardados correctamente")

            st.markdown("### 📊 Resumen de carga")
            st.write(f"Filas cargadas: {len(df)}")
            st.write(f"Columnas: {len(df.columns)}")
            st.write(f"Tabla: {nombre_tabla}")

        except Exception as e:
            st.error(f"Error al guardar: {e}")

# =========================
# VISUALIZAR DATOS
# =========================
st.markdown("---")
st.subheader("👁️ Visualizar datos en base")

if st.button("Ver registros guardados"):

    try:
        conn = sqlite3.connect(DB_NAME)

        tablas = pd.read_sql(
            "SELECT name FROM sqlite_master WHERE type='table';",
            conn
        )

        if tablas.empty:
            st.warning("No hay tablas en la base")
        else:
            st.write("Tablas disponibles:")
            st.write(tablas)

            tabla_sel = st.selectbox("Selecciona tabla", tablas["name"])

            df_db = pd.read_sql(f"SELECT * FROM {tabla_sel} LIMIT 100", conn)

            st.success(f"Filas mostradas: {len(df_db)}")

            st.dataframe(df_db)

        conn.close()

    except Exception as e:
        st.error(f"Error al leer la base: {e}")
