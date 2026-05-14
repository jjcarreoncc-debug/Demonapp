import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

from sigem_db import get_db_path


# =====================================================
# ASEGURAR COLUMNA CODIGO_TRANSPORTE EN INCIDENCIAS
# =====================================================

def asegurar_columna_codigo_transporte():

    db_path = get_db_path("logistica")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("PRAGMA table_info(incidencias)")
    columnas = [col[1] for col in cur.fetchall()]

    if "codigo_transporte" not in columnas:
        cur.execute("""
            ALTER TABLE incidencias
            ADD COLUMN codigo_transporte TEXT
        """)

    conn.commit()
    conn.close()


# =====================================================
# OBTENER TRANSPORTES
# =====================================================

def obtener_transportes():

    db_path = get_db_path("logistica")
    conn = sqlite3.connect(db_path)

    query = """
        SELECT
            codigo_transporte,
            codigo_ruta,
            ruta,
            transportista,
            vehiculo,
            placas,
            operador,
            estatus,
            COUNT(folio_embarque) AS total_embarques,
            GROUP_CONCAT(folio_embarque, ', ') AS embarques,
            GROUP_CONCAT(folio_hoja_carga, ', ') AS hojas_carga,
            GROUP_CONCAT(pedido, ', ') AS pedidos,
            GROUP_CONCAT(cliente, ', ') AS clientes,
            GROUP_CONCAT(destino, ', ') AS destinos,
            MAX(fecha) AS fecha
        FROM embarques
        WHERE codigo_transporte IS NOT NULL
          AND TRIM(codigo_transporte) <> ''
        GROUP BY
            codigo_transporte,
            codigo_ruta,
            ruta,
            transportista,
            vehiculo,
            placas,
            operador,
            estatus
        ORDER BY fecha DESC, codigo_transporte DESC
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

    asegurar_columna_codigo_transporte()

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
            codigo_transporte,
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
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, datos)

    conn.commit()
    conn.close()


# =====================================================
# APP
# =====================================================

def alta_incidencia_app():

    st.subheader("➕ Alta incidencia")

    st.info(
        "Registra incidencias operativas relacionadas con el transporte, "
        "incluyendo sus embarques, hojas de carga, ruta y proceso logístico."
    )

    try:

        asegurar_columna_codigo_transporte()
        df_transportes = obtener_transportes()

    except Exception as e:

        st.error("❌ Error consultando transportes.")
        st.exception(e)
        return

    if df_transportes.empty:

        st.warning("No existen transportes registrados.")
        return

    df_transportes = df_transportes.fillna("")

    df_transportes["opcion"] = (
        df_transportes["codigo_transporte"].astype(str)
        + " | "
        + df_transportes["transportista"].astype(str)
        + " | "
        + df_transportes["operador"].astype(str)
        + " | "
        + df_transportes["estatus"].astype(str)
    )

    opcion_transporte = st.selectbox(
        "Selecciona transporte relacionado",
        df_transportes["opcion"].tolist()
    )

    codigo_transporte = opcion_transporte.split(" | ")[0].strip()

    transporte = df_transportes[
        df_transportes["codigo_transporte"].astype(str).str.strip()
        == codigo_transporte
    ].iloc[0]

    st.divider()

    st.subheader("🚚 Datos del transporte")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.write("**Código transporte:**", transporte.get("codigo_transporte", ""))
        st.write("**Ruta:**", transporte.get("ruta", ""))
        st.write("**Código ruta:**", transporte.get("codigo_ruta", ""))

    with c2:
        st.write("**Transportista:**", transporte.get("transportista", ""))
        st.write("**Vehículo:**", transporte.get("vehiculo", ""))
        st.write("**Placas:**", transporte.get("placas", ""))

    with c3:
        st.write("**Operador:**", transporte.get("operador", ""))
        st.write("**Estatus:**", transporte.get("estatus", ""))
        st.write("**Total embarques:**", transporte.get("total_embarques", 0))

    st.markdown("### 📦 Embarques incluidos en el transporte")

    st.write("**Embarques:**", transporte.get("embarques", ""))
    st.write("**Hojas de carga:**", transporte.get("hojas_carga", ""))
    st.write("**Pedidos:**", transporte.get("pedidos", ""))
    st.write("**Clientes:**", transporte.get("clientes", ""))
    st.write("**Destinos:**", transporte.get("destinos", ""))

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
                "Transporte",
                "Ruta",
                "Entrega",
                "Hoja de carga",
                "Embarque",
                "Pedido",
                "Almacén",
                "Otro"
            ],
            index=0
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
                codigo_transporte,
                codigo_transporte,
                transporte.get("embarques", ""),
                transporte.get("hojas_carga", ""),
                transporte.get("pedidos", ""),
                transporte.get("clientes", ""),
                transporte.get("destinos", ""),
                transporte.get("transportista", ""),
                transporte.get("vehiculo", ""),
                transporte.get("placas", ""),
                transporte.get("operador", ""),
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
                f"✅ Incidencia registrada correctamente para el transporte {codigo_transporte}: {folio_incidencia}"
            )

        except Exception as e:

            st.error("❌ Error registrando incidencia.")
            st.exception(e)
