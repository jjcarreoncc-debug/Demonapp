import streamlit as st
import pandas as pd
import sqlite3
from sigem_db import get_db_path


st.set_page_config(
    page_title="SIGEM",
    page_icon="📦",
    layout="wide"
)

# ======================================================
# CONEXION BD
# ======================================================

def get_conn_logistica():
    conn = sqlite3.connect(get_db_path("logistica"))
    conn.row_factory = sqlite3.Row
    return conn


# ======================================================
# APP
# ======================================================

def consulta_clientes_logistica_app():

    st.title("🚚 Consulta Clientes - Logística")

    conn = get_conn_logistica()

    # ======================================================
    # FILTROS
    # ======================================================

    col1, col2, col3 = st.columns(3)

    with col1:
        filtro_cliente = st.text_input(
            "🔎 Buscar Cliente"
        )

    with col2:
        filtro_ciudad = st.text_input(
            "🏙️ Ciudad"
        )

    with col3:
        filtro_estado = st.text_input(
            "📍 Estado"
        )

    # ======================================================
    # QUERY
    # ======================================================

    query = """
        SELECT
            codigo_cliente,
            nombre_cliente,
            razon_social,
            ciudad,
            estado,
            pais,
            ruta,
            contacto_entrega,
            telefono_contacto,
            correo_contacto,
            direccion_entrega,
            colonia,
            codigo_postal,
            dias_entrega_permitidos,
            hora_inicio_recepcion,
            hora_fin_recepcion,
            requiere_cita,
            permite_entrega_parcial,
            restriccion_unidad,
            tipo_unidad_permitida,
            tiempo_descarga_min,
            peso_max_tarima,
            altura_max_tarima,
            permite_tarima_mixta,
            requiere_emplaye,
            requiere_etiqueta,
            tipo_tarima,
            gps_obligatorio,
            prioridad_ruta,
            cliente_critico,
            nivel_servicio,
            observaciones_logisticas,
            estatus
        FROM clientes
        WHERE 1=1
    """

    params = []

    # ======================================================
    # FILTROS DINAMICOS
    # ======================================================

    if filtro_cliente:
        query += """
            AND (
                nombre_cliente LIKE ?
                OR codigo_cliente LIKE ?
                OR razon_social LIKE ?
            )
        """

        valor = f"%{filtro_cliente}%"

        params.extend([
            valor,
            valor,
            valor
        ])

    if filtro_ciudad:
        query += " AND ciudad LIKE ? "
        params.append(f"%{filtro_ciudad}%")

    if filtro_estado:
        query += " AND estado LIKE ? "
        params.append(f"%{filtro_estado}%")

    query += " ORDER BY nombre_cliente "

    # ======================================================
    # DATAFRAME
    # ======================================================

    try:

        df = pd.read_sql_query(
            query,
            conn,
            params=params
        )

        if df.empty:

            st.warning(
                "No se encontraron clientes."
            )

        else:

            st.success(
                f"Clientes encontrados: {len(df)}"
            )

            st.dataframe(
                df,
                use_container_width=True,
                height=600
            )

            # ======================================================
            # EXPORTAR
            # ======================================================

            csv = df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="📥 Descargar CSV",
                data=csv,
                file_name="clientes_logistica.csv",
                mime="text/csv"
            )

    except Exception as e:

        st.error(
            f"Error al consultar clientes: {e}"
        )

    finally:

        conn.close()
