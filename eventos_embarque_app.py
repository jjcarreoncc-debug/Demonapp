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
# OBTENER EVENTOS EMBARQUE
# =====================================================

def obtener_eventos_embarque(folio_embarque):

    db_path = get_db_path("logistica")

    conn = sqlite3.connect(db_path)

    query = """
        SELECT
            id_evento,
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
        ORDER BY fecha_evento ASC, id_evento ASC
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
        SELECT estatus
        FROM embarques
        WHERE folio_embarque = ?
    """, (folio_embarque,))

    row = cur.fetchone()

    estatus_anterior = row[0] if row else ""

    # ==========================================
    # INSERT EVENTO
    # ==========================================

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

    # ==========================================
    # UPDATE EMBARQUE
    # ==========================================

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

    # ==========================================
    # HISTORIAL
    # ==========================================

    cur.execute("""
        INSERT INTO historial_estatus_embarque (
            folio_embarque,
            estatus_anterior,
            estatus_nuevo,
            fecha_cambio,
            usuario,
            observaciones
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        folio_embarque,
        estatus_anterior,
        estatus,
        fecha_evento,
        usuario,
        comentarios
    ))

    conn.commit()
    conn.close()


# =====================================================
# TIMELINE VISUAL
# =====================================================

# =====================================================
# TIMELINE VISUAL CON ALTAIR
# =====================================================

def pintar_timeline_visual(df_eventos):

    colores = {
        "Pendiente": "#6B7280",
        "En almacén": "#7C3AED",
        "En patio": "#F97316",
        "Ya salió": "#EAB308",
        "En tránsito": "#2563EB",
        "Entregado": "#16A34A",
        "Cancelado": "#DC2626"
    }

    orden_estatus = [
        "Pendiente",
        "En almacén",
        "En patio",
        "Ya salió",
        "En tránsito",
        "Entregado",
        "Cancelado"
    ]

    df_timeline = df_eventos.copy()

    df_timeline["fecha_evento"] = pd.to_datetime(
        df_timeline["fecha_evento"],
        errors="coerce"
    )

    df_timeline["estatus"] = (
        df_timeline["estatus"]
        .fillna("Pendiente")
        .astype(str)
    )

    df_timeline["evento"] = (
        df_timeline["tipo_evento"]
        .fillna("")
        .astype(str)
    )

    df_timeline["detalle"] = (
        df_timeline["estatus"].astype(str)
        + " | "
        + df_timeline["evento"].astype(str)
    )

    df_timeline = df_timeline.dropna(
        subset=["fecha_evento"]
    )

    if df_timeline.empty:

        st.info("No hay eventos válidos para mostrar en timeline.")
        return

    colores_usados = [
        colores.get(estatus, "#9CA3AF")
        for estatus in orden_estatus
    ]

    chart = (
        alt.Chart(df_timeline)
        .mark_circle(
            size=260,
            opacity=0.95
        )
        .encode(
            x=alt.X(
                "fecha_evento:T",
                title="Fecha / hora evento",
                axis=alt.Axis(
                    format="%d/%m %H:%M",
                    labelAngle=-45,
                    grid=True
                )
            ),
            y=alt.Y(
                "estatus:N",
                sort=orden_estatus,
                title="Estatus",
                axis=alt.Axis(
                    grid=True,
                    tickSize=0
                )
            ),
            color=alt.Color(
                "estatus:N",
                scale=alt.Scale(
                    domain=orden_estatus,
                    range=colores_usados
                ),
                legend=None
            ),
            tooltip=[
                alt.Tooltip("fecha_evento:T", title="Fecha evento"),
                alt.Tooltip("tipo_evento:N", title="Tipo evento"),
                alt.Tooltip("estatus:N", title="Estatus"),
                alt.Tooltip("ubicacion:N", title="Ubicación"),
                alt.Tooltip("comentarios:N", title="Comentarios"),
                alt.Tooltip("usuario:N", title="Usuario"),
                alt.Tooltip("latitud:Q", title="Latitud"),
                alt.Tooltip("longitud:Q", title="Longitud")
            ]
        )
        .properties(
            height=420
        )
        .configure_axis(
            grid=True,
            gridColor="#D1D5DB",
            gridDash=[3, 2],
            domain=False,
            labelColor="#374151",
            titleColor="#111827"
        )
        .configure_view(
            stroke="#D1D5DB"
        )
    )

    st.altair_chart(
        chart,
        use_container_width=True
    )
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
        df_embarques["folio_embarque"].astype(str)
        == folio_seleccionado
    ].iloc[0]

    st.divider()

    # =====================================================
    # DATOS EMBARQUE
    # =====================================================

    st.subheader("📦 Datos del embarque")

    c1, c2, c3 = st.columns(3)

    with c1:

        st.write(
            "**Folio:**",
            embarque.get("folio_embarque", "")
        )

        st.write(
            "**Cliente:**",
            embarque.get("cliente", "")
        )

        st.write(
            "**Destino:**",
            embarque.get("destino", "")
        )

    with c2:

        st.write(
            "**Transportista:**",
            embarque.get("transportista", "")
        )

        st.write(
            "**Vehículo:**",
            embarque.get("vehiculo", "")
        )

        st.write(
            "**Placas:**",
            embarque.get("placas", "")
        )

    with c3:

        st.write(
            "**Operador:**",
            embarque.get("operador", "")
        )

        st.write(
            "**Ruta:**",
            embarque.get("ruta", "")
        )

        st.write(
            "**Estatus actual:**",
            embarque.get("estatus", "")
        )

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

    estatus_actual = str(
        embarque.get("estatus", "") or ""
    )

    if estatus_actual in estatus_lista:

        index_estatus = estatus_lista.index(
            estatus_actual
        )

    else:

        index_estatus = 0

    col1, col2, col3 = st.columns(3)

    with col1:

        fecha_evento = st.date_input(
            "Fecha evento",
            value=datetime.now().date()
        )

    with col2:

        hora_evento = st.time_input(
            "Hora evento",
            value=datetime.now().time().replace(
                microsecond=0
            )
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
            estatus_lista,
            index=index_estatus
        )

    ubicacion = st.text_input(
        "Ubicación",
        placeholder="Ej. Patio CEDIS..."
    )

    comentarios = st.text_area(
        "Comentarios",
        placeholder="Describe el evento..."
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
                f"✅ Evento registrado para {folio_seleccionado}"
            )

            st.rerun()

        except Exception as e:

            st.error(
                "❌ Error registrando evento"
            )

            st.exception(e)

    st.divider()

    # =====================================================
    # TIMELINE
    # =====================================================

    st.subheader("📋 Timeline del embarque")

    try:

        df_eventos = obtener_eventos_embarque(
            folio_seleccionado
        )

        if df_eventos.empty:

            st.info(
                "Este embarque aún no tiene eventos."
            )

        else:

            tab1, tab2 = st.tabs([
                "🧭 Timeline visual",
                "📄 Tabla eventos"
            ])

            with tab1:

                pintar_timeline_visual(
                    df_eventos
                )

            with tab2:

                st.dataframe(
                    df_eventos,
                    use_container_width=True,
                    height=350,
                    hide_index=True
                )

    except Exception as e:

        st.error(
            "❌ Error consultando eventos"
        )

        st.exception(e)
