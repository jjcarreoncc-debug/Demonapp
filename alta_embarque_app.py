
import streamlit as st
import sqlite3
import pandas as pd

from datetime import date, datetime

from sigem_db import get_db_path


COLUMNAS_EXCEL_REQUERIDAS = [
    "folio_embarque",
    "folio_hoja_carga",
    "fecha",
    "cliente",
    "destino",
    "transportista",
    "vehiculo",
    "operador",
    "ruta",
    "estatus",
    "codigo_material",
    "descripcion",
    "cantidad_embarcar",
    "peso",
    "volumen",
    "bodega",
    "ubicacion",
    "observaciones",
    "usuario"
]


def limpiar_dataframe_excel(df):

    df.columns = [
        str(col).strip().lower()
        for col in df.columns
    ]

    for col in COLUMNAS_EXCEL_REQUERIDAS:
        if col not in df.columns:
            df[col] = ""

    df = df[COLUMNAS_EXCEL_REQUERIDAS].copy()

    df["folio_embarque"] = df["folio_embarque"].astype(str).str.strip()
    df["folio_hoja_carga"] = df["folio_hoja_carga"].astype(str).str.strip()
    df["codigo_material"] = df["codigo_material"].astype(str).str.strip()
    df["descripcion"] = df["descripcion"].astype(str).str.strip()

    df["cantidad_embarcar"] = pd.to_numeric(
        df["cantidad_embarcar"],
        errors="coerce"
    ).fillna(0)

    df["peso"] = pd.to_numeric(
        df["peso"],
        errors="coerce"
    ).fillna(0)

    df["volumen"] = pd.to_numeric(
        df["volumen"],
        errors="coerce"
    ).fillna(0)

    df = df[df["folio_embarque"] != ""]
    df = df[df["codigo_material"] != ""]

    return df


def validar_columnas_excel(df):

    columnas_archivo = [
        str(col).strip().lower()
        for col in df.columns
    ]

    faltantes = [
        col for col in COLUMNAS_EXCEL_REQUERIDAS
        if col not in columnas_archivo
    ]

    return faltantes


def guardar_embarque_manual(
    folio_embarque,
    folio_hoja_carga,
    fecha,
    cliente,
    destino,
    transportista,
    vehiculo,
    operador,
    ruta,
    estatus,
    observaciones,
    usuario
):

    conn = sqlite3.connect(get_db_path("logistica"))
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO embarques (
            folio_embarque,
            folio_hoja_carga,
            origen_captura,
            fecha,
            cliente,
            destino,
            transportista,
            vehiculo,
            operador,
            ruta,
            estatus,
            observaciones,
            usuario,
            fecha_creacion
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        folio_embarque,
        folio_hoja_carga,
        "MANUAL",
        fecha,
        cliente,
        destino,
        transportista,
        vehiculo,
        operador,
        ruta,
        estatus,
        observaciones,
        usuario,
        datetime.now()
    ))

    conn.commit()
    conn.close()


def guardar_embarques_excel(df):

    conn = sqlite3.connect(get_db_path("logistica"))
    cur = conn.cursor()

    embarques_insertados = 0
    detalles_insertados = 0
    embarques_existentes = 0

    embarques_header = df.drop_duplicates(
        subset=["folio_embarque"]
    )

    for _, row in embarques_header.iterrows():

        try:
            cur.execute("""
                INSERT INTO embarques (
                    folio_embarque,
                    folio_hoja_carga,
                    origen_captura,
                    fecha,
                    cliente,
                    destino,
                    transportista,
                    vehiculo,
                    operador,
                    ruta,
                    estatus,
                    observaciones,
                    usuario,
                    fecha_creacion
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row.get("folio_embarque", ""),
                row.get("folio_hoja_carga", ""),
                "EXCEL",
                str(row.get("fecha", "")),
                row.get("cliente", ""),
                row.get("destino", ""),
                row.get("transportista", ""),
                row.get("vehiculo", ""),
                row.get("operador", ""),
                row.get("ruta", ""),
                row.get("estatus", "Pendiente"),
                row.get("observaciones", ""),
                row.get("usuario", "admin"),
                datetime.now()
            ))

            embarques_insertados += 1

        except sqlite3.IntegrityError:
            embarques_existentes += 1

    for _, row in df.iterrows():

        cur.execute("""
            INSERT INTO detalle_embarque (
                folio_embarque,
                folio_hoja_carga,
                codigo_material,
                descripcion,
                cantidad_embarcar,
                peso,
                volumen,
                bodega,
                ubicacion
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row.get("folio_embarque", ""),
            row.get("folio_hoja_carga", ""),
            row.get("codigo_material", ""),
            row.get("descripcion", ""),
            row.get("cantidad_embarcar", 0),
            row.get("peso", 0),
            row.get("volumen", 0),
            row.get("bodega", ""),
            row.get("ubicacion", "")
        ))

        detalles_insertados += 1

    conn.commit()
    conn.close()

    return embarques_insertados, embarques_existentes, detalles_insertados


def alta_embarque_app():

    st.title("➕ Alta embarque")

    st.caption(
        "Hoja carga → Embarque → Tracking → Entrega"
    )

    st.divider()

    tab1, tab2 = st.tabs([
        "📝 Captura manual",
        "📤 Carga Excel"
    ])

    with tab1:

        with st.form("form_alta_embarque"):

            st.subheader("📦 Datos generales")

            col1, col2 = st.columns(2)

            with col1:
                folio_embarque = st.text_input("Folio embarque")
                folio_hoja_carga = st.text_input("Folio hoja carga")
                fecha = st.date_input("Fecha", value=date.today())
                cliente = st.text_input("Cliente")

            with col2:
                destino = st.text_input("Destino")

                estatus = st.selectbox(
                    "Estatus",
                    [
                        "Pendiente",
                        "Preparación",
                        "En ruta",
                        "Entregado",
                        "Cancelado"
                    ]
                )

                usuario = st.text_input(
                    "Usuario",
                    value="admin"
                )

            st.subheader("🚛 Transporte")

            col3, col4 = st.columns(2)

            with col3:
                transportista = st.text_input("Transportista")
                vehiculo = st.text_input("Vehículo")

            with col4:
                operador = st.text_input("Operador")
                ruta = st.text_input("Ruta")

            observaciones = st.text_area("Observaciones")

            guardar = st.form_submit_button("💾 Guardar embarque")

        if guardar:

            if not folio_embarque:
                st.warning("Captura el folio del embarque.")
                st.stop()

            try:
                guardar_embarque_manual(
                    folio_embarque,
                    folio_hoja_carga,
                    fecha,
                    cliente,
                    destino,
                    transportista,
                    vehiculo,
                    operador,
                    ruta,
                    estatus,
                    observaciones,
                    usuario
                )

                st.success("✅ Embarque registrado correctamente.")

            except sqlite3.IntegrityError:
                st.error("❌ Ese folio de embarque ya existe.")

            except Exception as e:
                st.error("❌ Error guardando embarque.")
                st.exception(e)

    with tab2:

        st.subheader("📤 Carga masiva embarques")

        st.info(
            "El Excel puede contener múltiples embarques. "
            "La app agrupa por folio_embarque y crea el detalle por cada material."
        )

        archivo_excel = st.file_uploader(
            "Subir archivo Excel",
            type=["xlsx"]
        )

        if archivo_excel is not None:

            try:
                df_original = pd.read_excel(archivo_excel)

                faltantes = validar_columnas_excel(df_original)

                if faltantes:
                    st.error("❌ El Excel no trae todas las columnas requeridas.")
                    st.write("Columnas faltantes:", faltantes)
                    st.write("Columnas detectadas:", df_original.columns.tolist())
                    st.stop()

                df = limpiar_dataframe_excel(df_original)

                if df.empty:
                    st.warning("El archivo no contiene registros válidos.")
                    st.stop()

                st.subheader("📋 Vista previa")

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

                total_registros = len(df)
                total_embarques = df["folio_embarque"].nunique()
                total_materiales = df["codigo_material"].nunique()

                c1, c2, c3 = st.columns(3)

                with c1:
                    st.metric("Registros", total_registros)

                with c2:
                    st.metric("Embarques", total_embarques)

                with c3:
                    st.metric("Materiales únicos", total_materiales)

                if st.button(
                    "💾 Guardar embarques",
                    use_container_width=True
                ):

                    (
                        embarques_insertados,
                        embarques_existentes,
                        detalles_insertados
                    ) = guardar_embarques_excel(df)

                    st.success("✅ Carga procesada correctamente.")

                    st.write(
                        "Embarques nuevos:",
                        embarques_insertados
                    )

                    st.write(
                        "Embarques ya existentes:",
                        embarques_existentes
                    )

                    st.write(
                        "Detalles insertados:",
                        detalles_insertados
                    )

            except Exception as e:
                st.error("❌ Error procesando Excel.")
                st.exception(e)
