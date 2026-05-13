
import streamlit as st
import sqlite3
import pandas as pd

from datetime import date, datetime

from sigem_db import get_db_path


# =====================================================
# GUARDAR EMBARQUE MANUAL
# =====================================================

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


# =====================================================
# GUARDAR EMBARQUES EXCEL
# =====================================================

def guardar_embarques_excel(df):

    conn = sqlite3.connect(get_db_path("logistica"))
    cur = conn.cursor()

    # ==========================================
    # CABECERAS
    # ==========================================

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

        except sqlite3.IntegrityError:
            pass

    # ==========================================
    # DETALLE
    # ==========================================

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

    conn.commit()
    conn.close()


# =====================================================
# APP
# =====================================================

def alta_embarque_app():

    st.title("➕ Alta embarque")

    st.caption(
        "Hoja carga → Embarque → Tracking → Entrega"
    )

    st.divider()

    # =====================================================
    # TABS
    # =====================================================

    tab1, tab2 = st.tabs([
        "📝 Captura manual",
        "📤 Carga Excel"
    ])

    # =====================================================
    # CAPTURA MANUAL
    # =====================================================

    with tab1:

        with st.form("form_alta_embarque"):

            st.subheader("📦 Datos generales")

            col1, col2 = st.columns(2)

            with col1:

                folio_embarque = st.text_input(
                    "Folio embarque"
                )

                folio_hoja_carga = st.text_input(
                    "Folio hoja carga"
                )

                fecha = st.date_input(
                    "Fecha",
                    value=date.today()
                )

                cliente = st.text_input(
                    "Cliente"
                )

            with col2:

                destino = st.text_input(
                    "Destino"
                )

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

                transportista = st.text_input(
                    "Transportista"
                )

                vehiculo = st.text_input(
                    "Vehículo"
                )

            with col4:

                operador = st.text_input(
                    "Operador"
                )

                ruta = st.text_input(
                    "Ruta"
                )

            observaciones = st.text_area(
                "Observaciones"
            )

            guardar = st.form_submit_button(
                "💾 Guardar embarque"
            )

        if guardar:

            if not folio_embarque:

                st.warning(
                    "Captura el folio del embarque."
                )

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

                st.success(
                    "✅ Embarque registrado correctamente."
                )

            except sqlite3.IntegrityError:

                st.error(
                    "❌ Ese folio de embarque ya existe."
                )

            except Exception as e:

                st.error(
                    "❌ Error guardando embarque."
                )

                st.exception(e)

    # =====================================================
    # CARGA EXCEL
    # =====================================================

    with tab2:

        st.subheader("📤 Carga masiva embarques")

        st.info(
            "El Excel puede contener múltiples embarques."
        )

        archivo_excel = st.file_uploader(
            "Subir archivo Excel",
            type=["xlsx"]
        )

        if archivo_excel is not None:

            try:

                df = pd.read_excel(archivo_excel)

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

                st.write(
                    "Total registros:",
                    len(df)
                )

                total_embarques = (
                    df["folio_embarque"]
                    .nunique()
                )

                st.write(
                    "Total embarques:",
                    total_embarques
                )

                if st.button(
                    "💾 Guardar embarques",
                    use_container_width=True
                ):

                    guardar_embarques_excel(df)

                    st.success(
                        f"✅ Embarques cargados correctamente ({total_embarques})"
                    )

            except Exception as e:

                st.error(
                    "❌ Error procesando Excel."
                )

                st.exception(e)
