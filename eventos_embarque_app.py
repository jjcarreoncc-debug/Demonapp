import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import altair as alt
from sigem_db import get_db_path


# =====================================================
# FLUJO CONTROLADO DE ESTATUS
# =====================================================

ESTATUS_LISTA_COMPLETA = [
    "Pendiente",
    "En almacén",
    "En patio",
    "Ya salió",
    "En tránsito",
    "Entregado",
    "Cancelado"
]

TRANSICIONES_VALIDAS = {
    "Pendiente": ["En almacén", "Cancelado"],
    "En almacén": ["En patio", "Cancelado"],
    "En patio": ["Ya salió", "Cancelado"],
    "Ya salió": ["En tránsito", "Cancelado"],
    "En tránsito": ["Entregado", "Cancelado"],
    "Entregado": [],
    "Cancelado": []
}


def obtener_siguientes_estatus(estatus_actual):

    estatus_actual = str(estatus_actual or "").strip()

    if not estatus_actual:
        estatus_actual = "Pendiente"

    return TRANSICIONES_VALIDAS.get(
        estatus_actual,
        []
    )


def validar_transicion_estatus(estatus_actual, estatus_nuevo):

    estatus_actual = str(estatus_actual or "").strip()
    estatus_nuevo = str(estatus_nuevo or "").strip()

    permitidos = obtener_siguientes_estatus(
        estatus_actual
    )

    return estatus_nuevo in permitidos


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
# OBTENER PUNTOS DE RUTA
# =====================================================

def obtener_puntos_ruta(codigo_ruta):

    db_path = get_db_path("logistica")
    conn = sqlite3.connect(db_path)

    query = """
        SELECT
            codigo_ruta,
            secuencia,
            tipo_punto,
            ubicacion,
            ciudad,
            estado,
            latitud,
            longitud
        FROM puntos_ruta
        WHERE codigo_ruta = ?
        ORDER BY secuencia ASC
    """

    df = pd.read_sql_query(
        query,
        conn,
        params=[codigo_ruta]
    )

    conn.close()

    return df


def obtener_punto_por_estatus(codigo_ruta, estatus):

    df_puntos = obtener_puntos_ruta(codigo_ruta)

    if df_puntos.empty:

        return {
            "ubicacion": "",
            "latitud": 0.0,
            "longitud": 0.0
        }

    estatus = str(estatus).strip()

    if estatus in ["Pendiente", "En almacén"]:

        punto = df_puntos.iloc[0]

    elif estatus == "En patio":

        puntos_patio = df_puntos[
            df_puntos["tipo_punto"]
            .fillna("")
            .str.lower()
            .str.contains("patio")
        ]

        if not puntos_patio.empty:
            punto = puntos_patio.iloc[0]
        elif len(df_puntos) >= 2:
            punto = df_puntos.iloc[1]
        else:
            punto = df_puntos.iloc[0]

    elif estatus in ["Ya salió", "En tránsito"]:

        if len(df_puntos) >= 2:
            punto = df_puntos.iloc[1]
        else:
            punto = df_puntos.iloc[0]

    elif estatus == "Entregado":

        punto = df_puntos.iloc[-1]

    elif estatus == "Cancelado":

        punto = df_puntos.iloc[0]

    else:

        punto = df_puntos.iloc[0]

    ubicacion = str(
        punto.get("ubicacion", "") or ""
    )

    ciudad = str(
        punto.get("ciudad", "") or ""
    )

    estado = str(
        punto.get("estado", "") or ""
    )

    if ciudad:
        ubicacion = f"{ubicacion} - {ciudad}"

    if estado:
        ubicacion = f"{ubicacion}, {estado}"

    return {
        "ubicacion": ubicacion,
        "latitud": float(
            punto.get("latitud", 0) or 0
        ),
        "longitud": float(
            punto.get("longitud", 0) or 0
        )
    }


# =====================================================
# OBTENER EVENTOS EMBARQUE
# =====================================================

def obtener_eventos_embarque(folio_embarque):

    db_path = get_db_path("logistica")
    conn = sqlite3.connect(db_path)

    query = """
        SELECT
            id_evento,
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
        FROM eventos_embarque
        WHERE TRIM(folio_embarque) = TRIM(?)
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

    fecha_registro = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cur.execute("""
        SELECT estatus
        FROM embarques
        WHERE TRIM(folio_embarque) = TRIM(?)
    """, (folio_embarque,))

    row = cur.fetchone()

    estatus_anterior = row[0] if row else ""

    estatus_anterior = str(
        estatus_anterior or ""
    ).strip()

    if not estatus_anterior:
        estatus_anterior = "Pendiente"

    estatus = str(
        estatus or ""
    ).strip()

    if estatus_anterior == estatus:

        conn.close()

        raise ValueError(
            f"El embarque ya se encuentra "
            f"en estatus '{estatus}'."
        )

    if not validar_transicion_estatus(
        estatus_anterior,
        estatus
    ):

        permitidos = obtener_siguientes_estatus(
            estatus_anterior
        )

        conn.close()

        raise ValueError(
            f"No se permite cambiar de "
            f"'{estatus_anterior}' a '{estatus}'. "
            f"Solo se permite avanzar a: "
            f"{', '.join(permitidos)}."
        )

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
        WHERE TRIM(folio_embarque) = TRIM(?)
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

    df_timeline = df_timeline.dropna(
        subset=["fecha_evento"]
    )

    if df_timeline.empty:

        st.info(
            "No hay eventos válidos para mostrar."
        )

        return

    df_timeline["estatus"] = (
        df_timeline["estatus"]
        .fillna("Pendiente")
        .astype(str)
    )

    df_timeline["orden_evento"] = range(
        1,
        len(df_timeline) + 1
    )

    colores_usados = [
        colores.get(estatus, "#9CA3AF")
        for estatus in orden_estatus
    ]

    linea = (
        alt.Chart(df_timeline)
        .mark_line(
            color="#9CA3AF",
            strokeWidth=3
        )
        .encode(
            x=alt.X(
                "orden_evento:O",
                title="Secuencia del evento"
            ),
            y=alt.Y(
                "estatus:N",
                sort=orden_estatus,
                title="Estatus"
            )
        )
    )

    puntos = (
        alt.Chart(df_timeline)
        .mark_circle(
            size=280
        )
        .encode(
            x=alt.X(
                "orden_evento:O",
                title="Secuencia del evento"
            ),
            y=alt.Y(
                "estatus:N",
                sort=orden_estatus,
                title="Estatus"
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
                alt.Tooltip(
                    "folio_embarque:N",
                    title="Folio"
                ),
                alt.Tooltip(
                    "fecha_evento:T",
                    title="Fecha evento"
                ),
                alt.Tooltip(
                    "tipo_evento:N",
                    title="Evento"
                ),
                alt.Tooltip(
                    "estatus:N",
                    title="Estatus"
                ),
                alt.Tooltip(
                    "ubicacion:N",
                    title="Ubicación"
                ),
                alt.Tooltip(
                    "comentarios:N",
                    title="Comentarios"
                ),
                alt.Tooltip(
                    "usuario:N",
                    title="Usuario"
                )
            ]
        )
    )

    chart = (
        (linea + puntos)
        .properties(
            height=420
        )
        .configure_axis(
            grid=True,
            gridColor="#D1D5DB",
            gridDash=[3, 2],
            domain=False
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
        "Cambia el estatus del embarque respetando "
        "la secuencia operativa. La ubicación y "
        "coordenadas se toman automáticamente de la "
        "ruta asignada."
    )

    try:

        df_embarques = obtener_embarques()

    except Exception as e:

        st.error(
            "❌ Error consultando embarques"
        )

        st.exception(e)

        return

    if df_embarques.empty:

        st.warning(
            "No existen embarques registrados."
        )

        return

    df_embarques["folio_embarque"] = (
        df_embarques["folio_embarque"]
        .astype(str)
        .str.strip()
    )

    df_embarques["estatus"] = (
        df_embarques["estatus"]
        .fillna("Pendiente")
        .astype(str)
        .str.strip()
    )

    df_embarques["opcion"] = (
        df_embarques["folio_embarque"]
        .astype(str)
        + " | "
        + df_embarques["cliente"]
        .fillna("")
        .astype(str)
        + " | "
        + df_embarques["destino"]
        .fillna("")
        .astype(str)
        + " | "
        + df_embarques["estatus"]
        .fillna("")
        .astype(str)
    )

    opciones_embarque = df_embarques["opcion"].tolist()

    if (
        "folio_eventos_seleccionado"
        not in st.session_state
    ):

        st.session_state[
            "folio_eventos_seleccionado"
        ] = opciones_embarque[0]

    if (
        st.session_state["folio_eventos_seleccionado"]
        not in opciones_embarque
    ):

        st.session_state[
            "folio_eventos_seleccionado"
        ] = opciones_embarque[0]

    opcion = st.selectbox(
        "Selecciona embarque",
        opciones_embarque,
        key="folio_eventos_seleccionado"
    )

    folio_seleccionado = (
        opcion.split(" | ")[0]
        .strip()
    )

    embarque = df_embarques[
        df_embarques["folio_embarque"]
        .astype(str)
        .str.strip()
        == folio_seleccionado
    ].iloc[0]

    codigo_ruta = str(
        embarque.get("ruta", "") or ""
    ).strip()

    estatus_actual = str(
        embarque.get("estatus", "") or ""
    ).strip()

    if not estatus_actual:
        estatus_actual = "Pendiente"

    siguientes_estatus = obtener_siguientes_estatus(
        estatus_actual
    )

    st.divider()

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
            codigo_ruta
        )

        st.write(
            "**Estatus actual:**",
            estatus_actual
        )

    st.divider()

    st.subheader(
        "➕ Registrar cambio de estatus"
    )

    if estatus_actual in ["Entregado", "Cancelado"]:

        st.success(
            f"✅ Este embarque ya se encuentra en "
            f"estatus final: {estatus_actual}"
        )

        st.info(
            "No hay más cambios de estatus disponibles."
        )

    elif not siguientes_estatus:

        st.warning(
            "⚠️ No hay una transición configurada "
            "para el estatus actual."
        )

    else:

        st.caption(
            f"El estatus actual es **{estatus_actual}**. "
            f"El siguiente permitido es: "
            f"**{', '.join(siguientes_estatus)}**"
        )

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

        estatus = st.selectbox(
            "Nuevo estatus",
            ESTATUS_LISTA_COMPLETA
        )

        tipo_evento = "Actualización de estatus"

        punto_ruta = obtener_punto_por_estatus(
            codigo_ruta,
            estatus
        )

        ubicacion = punto_ruta["ubicacion"]
        latitud = punto_ruta["latitud"]
        longitud = punto_ruta["longitud"]

        st.markdown(
            "### 📍 Datos automáticos de ruta"
        )

        col4, col5, col6 = st.columns(3)

        with col4:

            st.text_input(
                "Ubicación",
                value=ubicacion,
                disabled=True
            )

        with col5:

            st.number_input(
                "Latitud",
                value=latitud,
                format="%.6f",
                disabled=True
            )

        with col6:

            st.number_input(
                "Longitud",
                value=longitud,
                format="%.6f",
                disabled=True
            )

        comentarios = st.text_area(
            "Comentarios",
            placeholder="Describe el cambio de estatus..."
        )

        if not codigo_ruta:

            st.warning(
                "⚠️ Este embarque no tiene ruta asignada."
            )

        elif not ubicacion:

            st.warning(
                "⚠️ No se encontraron puntos de ruta "
                "para este embarque."
            )

        guardar = st.button(
            "💾 Guardar cambio de estatus",
            use_container_width=True
        )

        if guardar:

            try:

                if not codigo_ruta:

                    st.error(
                        "❌ No se puede registrar "
                        "el evento porque el embarque "
                        "no tiene ruta asignada."
                    )

                    return

                permitidos = obtener_siguientes_estatus(
                    estatus_actual
                )

                if estatus not in permitidos:

                    st.error(
                        "❌ No puede seleccionar este estatus "
                        "porque rompe la secuencia del proceso."
                    )

                    st.warning(
                        f"El embarque actualmente está en "
                        f"'{estatus_actual}'. "
                        f"Solo puede avanzar a: "
                        f"{', '.join(permitidos)}."
                    )

                    return

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
                    f"✅ Estatus actualizado "
                    f"para {folio_seleccionado}"
                )

                st.rerun()

            except Exception as e:

                st.error(
                    "❌ Error registrando evento"
                )

                st.exception(e)

    st.divider()

    st.subheader(
        "📋 Timeline del embarque"
    )

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
