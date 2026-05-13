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
# OBTENER HISTORIAL EVENTOS
# =====================================================

def obtener_eventos_embarque(folio_embarque):

    db_path = get_db_path("logistica")

    conn = sqlite3.connect(db_path)

    query = """
        SELECT
            fecha_evento,
            tipo_evento,
            estatus,
            ubicacion,
            comentarios,
            usuario,
            latitud,
            longitud,
            fecha_registro
        FROM eventos_embarque
        WHERE folio_embarque = ?
        ORDER BY fecha_evento DESC, id_evento DESC
    """

    df = pd.read_sql_query(
        query,
        conn,
        params=[folio_embarque]
    )

    conn.close()

    return df


# =====================================================
# REGISTRAR EVENTO
# =====================================================

def registrar_evento_embarque(
    folio_embarque,
    fecha_evento,
    tipo_evento,
    estatus,
    ubicacion,
    comentarios,
    usuario,
    latitud,
    longitud
):

    db_path = get_db_path("logistica")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("""
        INSERT INTO eventos_embarque (
            folio_embarque,
            fecha_evento,
            tipo_evento,
            estatus,
            ubicacion,
            comentarios,
            usuario,
            latitud,
            longitud,
            fecha_registro
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        folio_embarque,
        fecha_evento,
        tipo_evento,
        estatus,
        ubicacion,
        comentarios,
        usuario,
        latitud,
        longitud,
        fecha_registro
    ))

    cur.execute("""
        UPDATE embarques
        SET
            estatus = ?,
            fecha_estatus = ?,
            usuario_estatus = ?,
            observaciones_estatus = ?
        WHERE folio_embarque = ?
    """, (
        estatus,
        fecha_evento,
        usuario,
        comentarios,
        folio_embarque
    ))

    cur.execute("""
        INSERT INTO historial_estatus_embarque (
            folio_embarque,
            estatus_anterior,
            estatus_nuevo,
            fecha_cambio,
            usuario,
            observaciones
        )
        VALUES (
            ?,
            (
                SELECT estatus
                FROM embarques
                WHERE folio_embarque = ?
            ),
            ?,
            ?,
            ?,
            ?
        )
    """, (
        folio_embarque,
        folio_embarque,
        estatus,
        fecha_evento,
        usuario,
        comentarios
    ))

    conn.commit()
    conn.close()


# =====================================================
# APP
# =====================================================

def eventos_embarque_app():

    st.title("🛰️ Eventos embarque")

    st.info(
        "Registra eventos operativos del embarque y actualiza automáticamente su estatus."
    )

    try:

        df_embarques = obtener_embarques()

    except Exception as e:

        st.error("❌ Error consultando embarques")
        st.exception(e)
        return

    if df_embarques.empty:

        st.warning("No existen embarques registrados.")
        return

    # =====================================================
    # SELECCIONAR EMBARQUE
    # =====================================================

    df_embarques["opcion"] = (
        df_embarques["folio_embarque"].astype(str)
        + " | "
        + df_embarques["cliente"].fillna("").astype(str)
        + " | "
        + df_embarques["destino"].fillna("").astype(str)
        + " | "
        + df_embarques["estatus"].fillna("").astype(str)
    )

    opcion = st.selectbox(
        "Selecciona embarque",
        df_embarques["opcion"].tolist()
    )

    folio_seleccionado = opcion.split(" | ")[0]

    embarque = df_embarques[
        df_embarques["folio_embarque"].astype(str) == folio_seleccionado
    ].iloc[0]

    st.divider()

    # =====================================================
    # DATOS DEL EMBARQUE
    # =====================================================

    st.subheader("📦 Datos del embarque")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.write("**Folio:**", embarque.get("folio_embarque", ""))
        st.write("**Cliente:**", embarque.get("cliente", ""))
        st.write("**Destino:**", embarque.get("destino", ""))

    with c2:
        st.write("**Transportista:**", embarque.get("transportista", ""))
        st.write("**Vehículo:**", embarque.get("vehiculo", ""))
        st.write("**Placas:**", embarque.get("placas", ""))

    with c3:
        st.write("**Operador:**", embarque.get("operador", ""))
        st.write("**Ruta:**", embarque.get("ruta", ""))
        st.write("**Estatus actual:**", embarque.get("estatus", ""))

    st.divider()

    # =====================================================
    # CAPTURA EVENTO
    # =====================================================

    st.subheader("➕ Registrar evento")

    tipos_evento = [
        "Actualización de estatus",
        "Salida de almacén",
        "Llegada a patio",
        "Salida a ruta",
        "En tránsito",
        "Incidencia",
        "Retraso",
        "Llegada a destino",
        "Entrega confirmada",
        "POD recibido",
        "Cancelación"
    ]

    estatus_lista = [
        "Pendiente",
        "En almacén",
        "En patio",
        "Ya salió",
        "En tránsito",
        "Entregado",
        "Cancelado"
    ]

    col1, col2, col3 = st.columns(3)

    with col1:

        fecha_evento = st.date_input(
            "Fecha evento",
            value=datetime.now().date()
        )

    with col2:

        hora_evento = st.time_input(
            "Hora evento",
            value=datetime.now().time().replace(microsecond=0)
        )

    with col3:

        usuario = st.text_input(
            "Usuario",
            value="admin"
        )

    col4, col5 = st.columns(2)

    with col4:

        tipo_evento = st.selectbox(
            "Tipo evento",
            tipos_evento
        )

    with col5:

        estatus = st.selectbox(
            "Nuevo estatus",
            estatus_lista
        )

    ubicacion = st.text_input(
        "Ubicación",
        placeholder="Ej. Patio CEDIS, Caseta Tepotzotlán, Cliente, Ruta 57..."
    )

    comentarios = st.text_area(
        "Comentarios",
        placeholder="Describe el evento operativo..."
    )

    col6, col7 = st.columns(2)

    with col6:

        latitud = st.number_input(
            "Latitud",
            value=0.0,
            format="%.6f"
        )

    with col7:

        longitud = st.number_input(
            "Longitud",
            value=0.0,
            format="%.6f"
        )

    guardar = st.button(
        "💾 Guardar evento",
        use_container_width=True
    )

    if guardar:

        if not folio_seleccionado:

            st.warning("Selecciona un embarque.")

        elif not estatus:

            st.warning("Selecciona un estatus.")

        else:

            try:

                fecha_evento_completa = datetime.combine(
                    fecha_evento,
                    hora_evento
                ).strftime("%Y-%m-%d %H:%M:%S")

                registrar_evento_embarque(
                    folio_seleccionado,
                    fecha_evento_completa,
                    tipo_evento,
                    estatus,
                    ubicacion,
                    comentarios,
                    usuario,
                    latitud,
                    longitud
                )

                st.success(
                    f"✅ Evento registrado para embarque {folio_seleccionado}"
                )

                st.session_state.opcion_logistica = "🛰️ Eventos embarque"

                st.rerun()

            except Exception as e:

                st.error("❌ Error registrando evento")
                st.exception(e)

    st.divider()

    # =====================================================
    # TIMELINE / HISTORIAL
    # =====================================================

    st.subheader("📋 Timeline del embarque")

    try:

        df_eventos = obtener_eventos_embarque(
            folio_seleccionado
        )

        if df_eventos.empty:

            st.info("Este embarque aún no tiene eventos registrados.")

        else:

            st.dataframe(
                df_eventos,
                use_container_width=True,
                height=350,
                hide_index=True
            )

    except Exception as e:

        st.error("❌ Error consultando eventos del embarque")
        st.exception(e)
