import streamlit as st
import pandas as pd
import sqlite3
from sigem_db import get_db_path


def get_conn_logistica():
    conn = sqlite3.connect(get_db_path("logistica"))
    conn.row_factory = sqlite3.Row
    return conn


def es_si(valor):
    return str(valor).strip().lower() in ["si", "sí", "s", "1", "true", "x"]


def consulta_clientes_logistica_app():

    st.title("🚚 Consulta Clientes - Logística")

    conn = get_conn_logistica()

    try:
        with st.container(border=True):
            st.subheader("🔎 Filtros")

            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                filtro_cliente = st.text_input("Cliente")

            with col2:
                filtro_ciudad = st.text_input("Ciudad")

            with col3:
                filtro_estado = st.text_input("Estado")

            with col4:
                filtro_ruta = st.text_input("Ruta")

            with col5:
                filtro_estatus = st.selectbox(
                    "Estatus",
                    ["Todos", "Activo", "Inactivo"]
                )

        query = """
            SELECT
                codigo_cliente,
                nombre_cliente,
                razon_social,
                rfc,
                estatus,
                tipo_cliente,
                direccion_entrega,
                colonia,
                ciudad,
                estado,
                pais,
                codigo_postal,
                latitud,
                longitud,
                ruta,
                secuencia_ruta,
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
                contacto_entrega,
                telefono_contacto,
                correo_contacto,
                requiere_foto_entrega,
                requiere_firma,
                requiere_sello,
                gps_obligatorio,
                requiere_oc,
                requiere_factura_impresa,
                prioridad_ruta,
                cliente_critico,
                nivel_servicio,
                observaciones_logisticas
            FROM clientes
            WHERE 1=1
        """

        params = []

        if filtro_cliente:
            query += """
                AND (
                    codigo_cliente LIKE ?
                    OR nombre_cliente LIKE ?
                    OR razon_social LIKE ?
                    OR rfc LIKE ?
                )
            """
            valor = f"%{filtro_cliente}%"
            params.extend([valor, valor, valor, valor])

        if filtro_ciudad:
            query += " AND ciudad LIKE ? "
            params.append(f"%{filtro_ciudad}%")

        if filtro_estado:
            query += " AND estado LIKE ? "
            params.append(f"%{filtro_estado}%")

        if filtro_ruta:
            query += " AND ruta LIKE ? "
            params.append(f"%{filtro_ruta}%")

        if filtro_estatus != "Todos":
            query += " AND estatus = ? "
            params.append(filtro_estatus)

        query += " ORDER BY nombre_cliente "

        df = pd.read_sql_query(query, conn, params=params)

        if df.empty:
            st.warning("No se encontraron clientes.")
            return

        total_clientes = len(df)
        total_criticos = df["cliente_critico"].apply(es_si).sum()
        total_cita = df["requiere_cita"].apply(es_si).sum()
        total_gps = df["gps_obligatorio"].apply(es_si).sum()
        total_rutas = df["ruta"].fillna("").replace("", pd.NA).dropna().nunique()

        st.subheader("📊 Indicadores ejecutivos")

        k1, k2, k3, k4, k5 = st.columns(5)

        with k1:
            st.metric("👥 Clientes", total_clientes)

        with k2:
            st.metric("🚨 Críticos", int(total_criticos))

        with k3:
            st.metric("📅 Requieren cita", int(total_cita))

        with k4:
            st.metric("📡 GPS obligatorio", int(total_gps))

        with k5:
            st.metric("🚚 Rutas", int(total_rutas))

        st.divider()

        clientes_combo = (
            df["codigo_cliente"].astype(str)
            + " | "
            + df["nombre_cliente"].astype(str)
        )

        cliente_opcion = st.selectbox(
            "🧾 Cliente para consulta ejecutiva",
            clientes_combo.tolist()
        )

        codigo_sel = cliente_opcion.split(" | ")[0]

        cliente = df[
            df["codigo_cliente"].astype(str) == codigo_sel
        ].iloc[0]

        st.subheader("🧾 Consulta ejecutiva")

        encabezado1, encabezado2, encabezado3 = st.columns([2, 1, 1])

        with encabezado1:
            with st.container(border=True):
                st.subheader(cliente["nombre_cliente"])
                st.write(f"**Código:** {cliente['codigo_cliente']}")
                st.write(f"**Razón social:** {cliente['razon_social']}")
                st.write(f"**RFC:** {cliente['rfc']}")
                st.write(f"**Estatus:** {cliente['estatus']}")

        with encabezado2:
            with st.container(border=True):
                st.subheader("🚚 Ruta")
                st.metric("Ruta asignada", cliente["ruta"])
                st.write(f"**Secuencia:** {cliente['secuencia_ruta']}")
                st.write(f"**Prioridad:** {cliente['prioridad_ruta']}")

        with encabezado3:
            with st.container(border=True):
                st.subheader("⚠️ Alertas")
                st.write(f"**Cliente crítico:** {cliente['cliente_critico']}")
                st.write(f"**Requiere cita:** {cliente['requiere_cita']}")
                st.write(f"**GPS obligatorio:** {cliente['gps_obligatorio']}")
                st.write(f"**Nivel servicio:** {cliente['nivel_servicio']}")

        st.divider()

        c1, c2 = st.columns([2, 1])

        with c1:
            with st.container(border=True):
                st.subheader("📍 Resumen operativo")

                r1, r2, r3 = st.columns(3)

                with r1:
                    st.write("**Ubicación**")
                    st.write(f"{cliente['ciudad']}, {cliente['estado']}")
                    st.write(f"{cliente['pais']}")
                    st.write(f"C.P. {cliente['codigo_postal']}")

                with r2:
                    st.write("**Recepción**")
                    st.write(
                        f"{cliente['hora_inicio_recepcion']} - "
                        f"{cliente['hora_fin_recepcion']}"
                    )
                    st.write(f"Días: {cliente['dias_entrega_permitidos']}")
                    st.write(f"Descarga: {cliente['tiempo_descarga_min']} min")

                with r3:
                    st.write("**Entrega**")
                    st.write(f"Parcial: {cliente['permite_entrega_parcial']}")
                    st.write(f"Tarima mixta: {cliente['permite_tarima_mixta']}")
                    st.write(f"Tipo tarima: {cliente['tipo_tarima']}")

                st.info(
                    f"📝 Observaciones: {cliente['observaciones_logisticas']}"
                )

        with c2:
            with st.container(border=True):
                st.subheader("📞 Contacto")
                st.write(f"**Contacto:** {cliente['contacto_entrega']}")
                st.write(f"**Teléfono:** {cliente['telefono_contacto']}")
                st.write(f"**Correo:** {cliente['correo_contacto']}")
                st.write("**Dirección:**")
                st.write(cliente["direccion_entrega"])
                st.write(f"Colonia: {cliente['colonia']}")

        st.divider()

        tab1, tab2, tab3, tab4 = st.tabs(
            [
                "🚚 Restricciones",
                "📦 Requisitos entrega",
                "📍 Geografía",
                "📋 Grid detalle"
            ]
        )

        with tab1:
            r1, r2, r3, r4 = st.columns(4)

            with r1:
                st.metric("Requiere cita", cliente["requiere_cita"])

            with r2:
                st.metric("Unidad permitida", cliente["tipo_unidad_permitida"])

            with r3:
                st.metric("Peso máx tarima", cliente["peso_max_tarima"])

            with r4:
                st.metric("Altura máx tarima", cliente["altura_max_tarima"])

            with st.container(border=True):
                st.write(f"**Restricción unidad:** {cliente['restriccion_unidad']}")
                st.write(f"**Tiempo descarga:** {cliente['tiempo_descarga_min']} min")
                st.write(f"**Prioridad ruta:** {cliente['prioridad_ruta']}")

        with tab2:
            e1, e2, e3, e4, e5 = st.columns(5)

            with e1:
                st.metric("Emplaye", cliente["requiere_emplaye"])

            with e2:
                st.metric("Etiqueta", cliente["requiere_etiqueta"])

            with e3:
                st.metric("Foto entrega", cliente["requiere_foto_entrega"])

            with e4:
                st.metric("Firma", cliente["requiere_firma"])

            with e5:
                st.metric("Sello", cliente["requiere_sello"])

            with st.container(border=True):
                st.write(f"**Requiere OC:** {cliente['requiere_oc']}")
                st.write(
                    f"**Requiere factura impresa:** "
                    f"{cliente['requiere_factura_impresa']}"
                )

        with tab3:
            g1, g2, g3 = st.columns(3)

            with g1:
                st.metric("Latitud", cliente["latitud"])

            with g2:
                st.metric("Longitud", cliente["longitud"])

            with g3:
                st.metric("GPS obligatorio", cliente["gps_obligatorio"])

            with st.container(border=True):
                st.write(f"**Ciudad:** {cliente['ciudad']}")
                st.write(f"**Estado:** {cliente['estado']}")
                st.write(f"**País:** {cliente['pais']}")
                st.write(f"**Código postal:** {cliente['codigo_postal']}")

        with tab4:
            columnas_grid = [
                "codigo_cliente",
                "nombre_cliente",
                "ciudad",
                "estado",
                "ruta",
                "estatus",
                "requiere_cita",
                "gps_obligatorio",
                "cliente_critico",
                "nivel_servicio",
                "contacto_entrega",
                "telefono_contacto"
            ]

            st.dataframe(
                df[columnas_grid],
                use_container_width=True,
                height=420
            )

            csv = df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="📥 Descargar CSV",
                data=csv,
                file_name="clientes_logistica.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"Error al consultar clientes: {e}")

    finally:
        conn.close()
