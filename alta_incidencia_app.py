import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

from sigem_db import get_db_path


# =====================================================
# OBTENER EMBARQUES
# =====================================================

def obtener_embarques():

    db_path = get_db_path("logistica")
    conn = sqlite3.connect(db_path)

    query = """
        SELECT
            folio_embarque,
            folio_hoja_carga,
            pedido,
            fecha,
            cliente,
            destino,
            transportista,
            vehiculo,
            placas,
            operador,
            ruta,
            estatus
        FROM embarques
        ORDER BY fecha DESC, folio_embarque DESC
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    return df


# =====================================================
# GENERAR FOLIO INCIDENCIA
# =====================================================

def generar_folio_incidencia():

    fecha = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"INC-{fecha}"


# =====================================================
# REGISTRAR INCIDENCIA
# =====================================================

def registrar_incidencia(datos):

    db_path = get_db_path("logistica")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO incidencias (
            folio_incidencia,
            fecha,
            modulo,
            proceso,
            tipo_incidencia,
            prioridad,
            estatus,
            folio_referencia,
            folio_embarque,
            folio_hoja_carga,
            pedido,
            cliente,
            destino,
            transportista,
            vehiculo,
            placas,
            operador,
            responsable,
            descripcion_incidencia,
            causa,
            solucion,
            usuario_registro,
            observaciones,
            fecha_creacion
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, datos)

    conn.commit()
    conn.close()


# =====================================================
# APP
# =====================================================

def alta_incidencia_app():

    st.subheader("➕ Alta incidencia")

    st.info(
        "Registra incidencias operativas relacionadas con embarques, "
        "hojas de carga, pedidos, transporte o proceso logístico."
    )

    try:

        df_embarques = obtener_embarques()

    except Exception as e:

        st.error("❌ Error consultando embarques.")
        st.exception(e)
        return

    if df_embarques.empty:

        st.warning("No existen embarques registrados.")
        return

    df_embarques = df_embarques.fillna("")

    df_embarques["opcion"] = (
        df_embarques["folio_embarque"].astype(str)
        + " | "
        + df_embarques["cliente"].astype(str)
        + " | "
        + df_embarques["destino"].astype(str)
        + " | "
        + df_embarques["estatus"].astype(str)
    )

    opcion_embarque = st.selectbox(
        "Selecciona embarque relacionado",
        df_embarques["opcion"].tolist()
    )

    folio_embarque = opcion_embarque.split(" | ")[0].strip()

    embarque = df_embarques[
        df_embarques["folio_embarque"].astype(str).str.strip()
        == folio_embarque
    ].iloc[0]

    st.divider()

    st.subheader("📦 Datos del embarque")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.write("**Folio embarque:**", embarque.get("folio_embarque", ""))
        st.write("**Hoja carga:**", embarque.get("folio_hoja_carga", ""))
        st.write("**Pedido:**", embarque.get("pedido", ""))

    with c2:
        st.write("**Cliente:**", embarque.get("cliente", ""))
        st.write("**Destino:**", embarque.get("destino", ""))
        st.write("**Estatus:**", embarque.get("estatus", ""))

    with c3:
        st.write("**Transportista:**", embarque.get("transportista", ""))
        st.write("**Vehículo:**", embarque.get("vehiculo", ""))
        st.write("**Operador:**", embarque.get("operador", ""))

    st.divider()

    st.subheader("📝 Datos de la incidencia")

    col1, col2, col3 = st.columns(3)

    with col1:

        fecha = st.date_input(
            "Fecha incidencia",
            value=datetime.now().date()
        )

    with col2:

        hora = st.time_input(
            "Hora incidencia",
            value=datetime.now().time().replace(microsecond=0)
        )

    with col3:

        usuario_registro = st.text_input(
            "Usuario registro",
            value="admin"
        )

    col4, col5, col6 = st.columns(3)

    with col4:

        proceso = st.selectbox(
            "Proceso",
            [
                "Embarque",
                "Hoja de carga",
                "Pedido",
                "Transporte",
                "Ruta",
                "Entrega",
                "Almacén",
                "Otro"
            ]
        )

    with col5:

        tipo_incidencia = st.selectbox(
            "Tipo incidencia",
            [
                "Retraso",
                "Falla mecánica",
                "Accidente",
                "Cliente cerrado",
                "Rechazo de entrega",
                "Daño de mercancía",
                "Faltante",
                "Documentación incompleta",
                "Desvío de ruta",
                "Error de surtido",
                "Error de embarque",
                "Otro"
            ]
        )

    with col6:

        prioridad = st.selectbox(
            "Prioridad",
            [
                "Baja",
                "Media",
                "Alta",
                "Crítica"
            ],
            index=1
        )

    responsable = st.text_input(
        "Responsable",
        placeholder="Ej. tráfico, almacén, transportista, operador..."
    )

    descripcion_incidencia = st.text_area(
        "Descripción de la incidencia",
        placeholder="Describe la incidencia encontrada..."
    )

    causa = st.text_area(
        "Causa probable",
        placeholder="Describe la causa probable si se conoce..."
    )

    observaciones = st.text_area(
        "Observaciones",
        placeholder="Comentarios adicionales..."
    )

    guardar = st.button(
        "💾 Guardar incidencia",
        use_container_width=True
    )

    if guardar:

        try:

            if not descripcion_incidencia.strip():

                st.warning("⚠️ Captura la descripción de la incidencia.")
                return

            folio_incidencia = generar_folio_incidencia()

            fecha_incidencia = datetime.combine(
                fecha,
                hora
            ).strftime("%Y-%m-%d %H:%M:%S")

            datos = (
                folio_incidencia,
                fecha_incidencia,
                "Logística",
                proceso,
                tipo_incidencia,
                prioridad,
                "Abierta",
                folio_embarque,
                embarque.get("folio_embarque", ""),
                embarque.get("folio_hoja_carga", ""),
                embarque.get("pedido", ""),
                embarque.get("cliente", ""),
                embarque.get("destino", ""),
                embarque.get("transportista", ""),
                embarque.get("vehiculo", ""),
                embarque.get("placas", ""),
                embarque.get("operador", ""),
                responsable,
                descripcion_incidencia,
                causa,
                "",
                usuario_registro,
                observaciones,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )

            registrar_incidencia(datos)

            st.success(
                f"✅ Incidencia registrada correctamente: {folio_incidencia}"
            )

        except Exception as e:

            st.error("❌ Error registrando incidencia.")
            st.exception(e)
