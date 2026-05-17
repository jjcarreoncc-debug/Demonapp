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

    conn = sqlite3.connect(
        get_db_path("logistica")
    )

    conn.row_factory = sqlite3.Row

    return conn


# ======================================================
# APP
# ======================================================

def consulta_clientes_logistica_app():

    st.title(
        "🚚 Consulta Clientes - Logística"
    )

    conn = get_conn_logistica()

    # ======================================================
    # FILTROS
    # ======================================================

    with st.container(border=True):

        st.subheader(
            "🔎 Filtros de búsqueda"
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            filtro_cliente = st.text_input(
                "Cliente"
            )

        with col2:

            filtro_ciudad = st.text_input(
                "Ciudad"
            )

        with col3:

            filtro_estado = st.text_input(
                "Estado"
            )

        with col4:

            filtro_estatus = st.selectbox(
                "Estatus",
                [
                    "Todos",
                    "Activo",
                    "Inactivo"
                ]
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

        query += """
            AND ciudad LIKE ?
        """

        params.append(
            f"%{filtro_ciudad}%"
        )

    if filtro_estado:

        query += """
            AND estado LIKE ?
        """

        params.append(
            f"%{filtro_estado}%"
        )

    if filtro_estatus != "Todos":

        query += """
            AND estatus = ?
        """

        params.append(
            filtro_estatus
        )

    query += """
        ORDER BY nombre_cliente
    """

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

            # ======================================================
            # KPIS
            # ======================================================

            total_clientes = len(df)

            clientes_criticos = len(
                df[
                    df["cliente_critico"]
                    .astype(str)
                    .str.lower()
                    .isin(["si", "sí", "1", "true"])
                ]
            )

            clientes_cita = len(
                df[
                    df["requiere_cita"]
                    .astype(str)
                    .str.lower()
                    .isin(["si", "sí", "1", "true"])
                ]
            )

            clientes_gps = len(
                df[
                    df["gps_obligatorio"]
                    .astype(str)
                    .str.lower()
                    .isin(["si", "sí", "1", "true"])
                ]
            )

            st.subheader(
                "📊 Indicadores ejecutivos"
            )

            k1, k2, k3, k4 = st.columns(4)

            with k1:

                st.metric(
                    "👥 Clientes",
                    total_clientes
                )

            with k2:

                st.metric(
                    "🚨 Clientes críticos",
                    clientes_criticos
                )

            with k3:

                st.metric(
                    "📅 Requiere cita",
                    clientes_cita
                )

            with k4:

                st.metric(
                    "📡 GPS obligatorio",
                    clientes_gps
                )

            st.divider()

            # ======================================================
            # CONSULTA EJECUTIVA
            # ======================================================

            st.subheader(
                "🧾 Consulta ejecutiva"
            )

            lista_clientes = (
                df["nombre_cliente"]
                .dropna()
                .unique()
                .tolist()
            )

            cliente_seleccionado = st.selectbox(
                "Selecciona cliente",
                lista_clientes
            )

            df_cliente = df[
                df["nombre_cliente"]
                == cliente_seleccionado
            ]

            if not df_cliente.empty:

                cliente = df_cliente.iloc[0]

                col1, col2 = st.columns(2)

                with col1:

                    st.info(
                        f"""
                        Código Cliente: {cliente['codigo_cliente']}
                        
                        Cliente: {cliente['nombre_cliente']}
                        
                        Razón Social: {cliente['razon_social']}
                        
                        Ciudad: {cliente['ciudad']}
                        
                        Estado: {cliente['estado']}
                        
                        Ruta: {cliente['ruta']}
                        """
                    )

                with col2:

                    st.success(
                        f"""
                        Nivel Servicio: {cliente['nivel_servicio']}
                        
                        Cliente Crítico: {cliente['cliente_critico']}
                        
                        GPS Obligatorio: {cliente['gps_obligatorio']}
                        
                        Requiere Cita: {cliente['requiere_cita']}
                        
                        Contacto: {cliente['contacto_entrega']}
                        
                        Teléfono: {cliente['telefono_contacto']}
                        """
                    )

                # ======================================================
                # TABS
                # ======================================================

                tab1, tab2, tab3 = st.tabs([
                    "📞 Contacto",
                    "🚚 Restricciones",
                    "📦 Logística"
                ])

                with tab1:

                    st.write(
                        "### 📞 Información contacto"
                    )

                    st.write(
                        f"Correo: {cliente['correo_contacto']}"
                    )

                    st.write(
                        f"Dirección: {cliente['direccion_entrega']}"
                    )

                    st.write(
                        f"Colonia: {cliente['colonia']}"
                    )

                    st.write(
                        f"Código Postal: {cliente['codigo_postal']}"
                    )

                with tab2:

                    st.write(
                        "### 🚚 Restricciones operativas"
                    )

                    st.write(
                        f"Restricción unidad: {cliente['restriccion_unidad']}"
                    )

                    st.write(
                        f"Tipo unidad: {cliente['tipo_unidad_permitida']}"
                    )

                    st.write(
                        f"Tiempo descarga: {cliente['tiempo_descarga_min']}"
                    )

                    st.write(
                        f"Peso máximo tarima: {cliente['peso_max_tarima']}"
                    )

                    st.write(
                        f"Altura máxima tarima: {cliente['altura_max_tarima']}"
                    )

                with tab3:

                    st.write(
                        "### 📦 Información logística"
                    )

                    st.write(
                        f"Días entrega: {cliente['dias_entrega_permitidos']}"
                    )

                    st.write(
                        f"Horario recepción: {cliente['hora_inicio_recepcion']} - {cliente['hora_fin_recepcion']}"
                    )

                    st.write(
                        f"Tipo tarima: {cliente['tipo_tarima']}"
                    )

                    st.write(
                        f"Prioridad ruta: {cliente['prioridad_ruta']}"
                    )

                    st.write(
                        f"Observaciones: {cliente['observaciones_logisticas']}"
                    )

            st.divider()

            # ======================================================
            # GRID
            # ======================================================

            st.subheader(
                "📋 Grid detalle clientes"
            )

            st.dataframe(
                df,
                use_container_width=True,
                height=500
            )

            # ======================================================
            # EXPORTAR
            # ======================================================

            csv = df.to_csv(
                index=False
            ).encode("utf-8")

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
