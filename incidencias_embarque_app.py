import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from sigem_db import get_db_path


# =====================================================
# CREAR TABLA INCIDENCIAS EMBARQUE
# =====================================================

def crear_tabla_incidencias_embarque():

    db_path = get_db_path("logistica")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS incidencias_embarque (
            id_incidencia INTEGER PRIMARY KEY AUTOINCREMENT,
            folio_embarque TEXT NOT NULL,
            fecha_incidencia TEXT NOT NULL,
            tipo_incidencia TEXT NOT NULL,
            severidad TEXT NOT NULL,
            estatus_incidencia TEXT NOT NULL,
            descripcion TEXT,
            responsable TEXT,
            usuario TEXT,
            fecha_registro TEXT
        )
    """)

    conn.commit()
    conn.close()


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
# REGISTRAR INCIDENCIA
# =====================================================

def registrar_incidencia_embarque(
    folio_embarque,
    fecha_incidencia,
    tipo_incidencia,
    severidad,
    estatus_incidencia,
    descripcion,
    responsable,
    usuario
):

    db_path = get_db_path("logistica")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    fecha_registro = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cur.execute("""
        INSERT INTO incidencias_embarque (
            folio_embarque,
            fecha_incidencia,
            tipo_incidencia,
            severidad,
            estatus_incidencia,
            descripcion,
            responsable,
            usuario,
            fecha_registro
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        folio_embarque,
        fecha_incidencia,
        tipo_incidencia,
        severidad,
        estatus_incidencia,
        descripcion,
        responsable,
        usuario,
        fecha_registro
    ))

    conn.commit()
    conn.close()


# =====================================================
# OBTENER INCIDENCIAS
# =====================================================

def obtener_incidencias_embarque(folio_embarque=None):

    db_path = get_db_path("logistica")
    conn = sqlite3.connect(db_path)

    if folio_embarque:

        query = """
            SELECT
                id_incidencia,
                folio_embarque,
                fecha_incidencia,
                tipo_incidencia,
                severidad,
                estatus_incidencia,
                descripcion,
                responsable,
                usuario,
                fecha_registro
            FROM incidencias_embarque
            WHERE TRIM(folio_embarque) = TRIM(?)
            ORDER BY fecha_incidencia DESC, id_incidencia DESC
        """

        df = pd.read_sql_query(
            query,
            conn,
            params=[folio_embarque]
        )

    else:

        query = """
            SELECT
                id_incidencia,
                folio_embarque,
                fecha_incidencia,
                tipo_incidencia,
                severidad,
                estatus_incidencia,
                descripcion,
                responsable,
                usuario,
                fecha_registro
            FROM incidencias_embarque
            ORDER BY fecha_incidencia DESC, id_incidencia DESC
        """

        df = pd.read_sql_query(query, conn)

    conn.close()

    return df


# =====================================================
# APP
# =====================================================

def incidencias_embarque_app():

    st.title("⚠️ Incidencias de embarque")

    st.info(
        "Registra, consulta y da seguimiento a incidencias "
        "operativas relacionadas con los embarques."
    )

    try:

        crear_tabla_incidencias_embarque()
        df_embarques = obtener_embarques()

    except Exception as e:

        st.error("❌ Error inicializando incidencias")
        st.exception(e)
        return

    if df_embarques.empty:

        st.warning("No existen embarques registrados.")
        return

    df_embarques["folio_embarque"] = (
        df_embarques["folio_embarque"]
        .astype(str)
        .str.strip()
    )

    df_embarques["estatus"] = (
        df_embarques["estatus"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df_embarques["opcion"] = (
        df_embarques["folio_embarque"]
        + " | "
        + df_embarques["cliente"].fillna("").astype(str)
        + " | "
        + df_embarques["destino"].fillna("").astype(str)
        + " | "
        + df_embarques["estatus"]
    )

    opcion = st.selectbox(
        "Selecciona embarque",
        df_embarques["opcion"].tolist()
    )

    folio_seleccionado = (
        opcion.split(" | ")[0]
        .strip()
    )

    embarque = df_embarques[
        df_embarques["folio_embarque"]
        == folio_seleccionado
    ].iloc[0]

    st.divider()

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
        st.write("**Estatus:**", embarque.get("estatus", ""))

    st.divider()

    tab1, tab2 = st.tabs([
        "➕ Registrar incidencia",
        "📋 Consultar incidencias"
    ])

    with tab1:

        st.subheader("➕ Nueva incidencia")

        col1, col2, col3 = st.columns(3)

        with col1:

            fecha = st.date_input(
                "Fecha incidencia",
                value=datetime.now().date()
            )

        with col2:

            hora = st.time_input(
                "Hora incidencia",
                value=datetime.now().time().replace(
                    microsecond=0
                )
            )

        with col3:

            usuario = st.text_input(
                "Usuario",
                value="admin"
            )

        col4, col5, col6 = st.columns(3)

        with col4:

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
                    "Otro"
                ]
            )

        with col5:

            severidad = st.selectbox(
                "Severidad",
                [
                    "Baja",
                    "Media",
                    "Alta",
                    "Crítica"
                ]
            )

        with col6:

            estatus_incidencia = st.selectbox(
                "Estatus incidencia",
                [
                    "Abierta",
                    "En seguimiento",
                    "Resuelta",
                    "Cancelada"
                ]
            )

        responsable = st.text_input(
            "Responsable",
            placeholder="Ej. tráfico, almacén, transportista..."
        )

        descripcion = st.text_area(
            "Descripción",
            placeholder="Describe la incidencia..."
        )

        guardar = st.button(
            "💾 Guardar incidencia",
            use_container_width=True
        )

        if guardar:

            try:

                if not descripcion.strip():

                    st.warning(
                        "⚠️ Captura una descripción de la incidencia."
                    )

                    return

                fecha_incidencia = datetime.combine(
                    fecha,
                    hora
                ).strftime("%Y-%m-%d %H:%M:%S")

                registrar_incidencia_embarque(
                    folio_seleccionado,
                    fecha_incidencia,
                    tipo_incidencia,
                    severidad,
                    estatus_incidencia,
                    descripcion,
                    responsable,
                    usuario
                )

                st.success(
                    f"✅ Incidencia registrada para "
                    f"{folio_seleccionado}"
                )

            except Exception as e:

                st.error("❌ Error registrando incidencia")
                st.exception(e)

    with tab2:

        st.subheader("📋 Incidencias del embarque")

        try:

            df_incidencias = obtener_incidencias_embarque(
                folio_seleccionado
            )

            if df_incidencias.empty:

                st.info(
                    "Este embarque no tiene incidencias registradas."
                )

            else:

                st.dataframe(
                    df_incidencias,
                    use_container_width=True,
                    height=350,
                    hide_index=True
                )

        except Exception as e:

            st.error("❌ Error consultando incidencias")
            st.exception(e)

    st.divider()

    st.subheader("📊 Resumen general de incidencias")

    try:

        df_todas = obtener_incidencias_embarque()

        if df_todas.empty:

            st.info("No hay incidencias registradas.")

        else:

            c1, c2, c3, c4 = st.columns(4)

            abiertas = len(
                df_todas[
                    df_todas["estatus_incidencia"]
                    == "Abierta"
                ]
            )

            seguimiento = len(
                df_todas[
                    df_todas["estatus_incidencia"]
                    == "En seguimiento"
                ]
            )

            resueltas = len(
                df_todas[
                    df_todas["estatus_incidencia"]
                    == "Resuelta"
                ]
            )

            criticas = len(
                df_todas[
                    df_todas["severidad"]
                    == "Crítica"
                ]
            )

            with c1:
                st.metric("Abiertas", abiertas)

            with c2:
                st.metric("En seguimiento", seguimiento)

            with c3:
                st.metric("Resueltas", resueltas)

            with c4:
                st.metric("Críticas", criticas)

            st.dataframe(
                df_todas,
                use_container_width=True,
                height=300,
                hide_index=True
            )

    except Exception as e:

        st.error("❌ Error generando resumen")
        st.exception(e)
