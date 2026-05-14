
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

from sigem_db import get_db_path


# =====================================================
# OBTENER TRANSPORTES
# =====================================================

def obtener_transportes_para_estatus():

    db_path = get_db_path("logistica")

    conn = sqlite3.connect(db_path)

    query = """
        SELECT
            codigo_transporte,
            MAX(folio_hoja_carga) AS folio_hoja_carga,
            MAX(folio_ruta) AS folio_ruta,
            MAX(fecha) AS fecha,
            transportista,
            vehiculo,
            placas,
            operador,
            ruta,
            estatus,
            GROUP_CONCAT(cliente, ', ') AS clientes,
            GROUP_CONCAT(destino, ', ') AS destinos,
            COUNT(folio_embarque) AS total_embarques,
            MAX(fecha_estatus) AS fecha_estatus,
            MAX(usuario_estatus) AS usuario_estatus,
            MAX(observaciones_estatus) AS observaciones_estatus
        FROM embarques
        WHERE
            codigo_transporte IS NOT NULL
            AND TRIM(codigo_transporte) <> ''
            AND UPPER(TRIM(estatus)) NOT IN (
                'ENTREGADO',
                'CANCELADO',
                'FINALIZADO',
                'FINALIZADA',
                'CONCLUIDO',
                'CONCLUIDA'
            )
        GROUP BY
            codigo_transporte,
            transportista,
            vehiculo,
            placas,
            operador,
            ruta,
            estatus
        ORDER BY fecha DESC, codigo_transporte DESC
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


# =====================================================
# OBTENER CATALOGO ESTATUS
# =====================================================

def obtener_catalogo_estatus():

    db_path = get_db_path("logistica")

    conn = sqlite3.connect(db_path)

    query = """
        SELECT
            descripcion
        FROM estatus_embarque
        WHERE activo = 1
        ORDER BY secuencia
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    if df.empty:

        return [
            "En almacén",
            "En patio",
            "Ya salió",
            "En tránsito",
            "Entregado",
            "Cancelado"
        ]

    return df["descripcion"].dropna().astype(str).tolist()


# =====================================================
# OBTENER DETALLE TRANSPORTE
# =====================================================

def obtener_detalle_transporte(codigo_transporte):

    db_path = get_db_path("logistica")

    conn = sqlite3.connect(db_path)

    query = """
        SELECT
            codigo_transporte,
            folio_embarque,
            pedido,
            codigo_material,
            descripcion,
            cantidad_pedida,
            cantidad_embarcar,
            peso,
            volumen,
            bodega,
            ubicacion
        FROM detalle_embarque
        WHERE codigo_transporte = ?
    """

    try:

        df = pd.read_sql_query(
            query,
            conn,
            params=[codigo_transporte]
        )

    except Exception:

        query = """
            SELECT
                e.codigo_transporte,
                d.folio_embarque,
                d.pedido,
                d.codigo_material,
                d.descripcion,
                d.cantidad_pedida,
                d.cantidad_embarcar,
                d.peso,
                d.volumen,
                d.bodega,
                d.ubicacion
            FROM detalle_embarque d
            LEFT JOIN embarques e
                ON d.folio_embarque = e.folio_embarque
            WHERE e.codigo_transporte = ?
        """

        df = pd.read_sql_query(
            query,
            conn,
            params=[codigo_transporte]
        )

    conn.close()

    return df


# =====================================================
# OBTENER HISTORIAL
# =====================================================

def obtener_historial_estatus(codigo_transporte):

    db_path = get_db_path("logistica")

    conn = sqlite3.connect(db_path)

    query = """
        SELECT
            folio_embarque,
            estatus_anterior,
            estatus_nuevo,
            fecha_cambio,
            usuario,
            observaciones
        FROM historial_estatus_embarque
        WHERE folio_embarque = ?
        ORDER BY fecha_cambio DESC
    """

    df = pd.read_sql_query(
        query,
        conn,
        params=[codigo_transporte]
    )

    conn.close()

    return df


# =====================================================
# ACTUALIZAR ESTATUS
# =====================================================

def actualizar_estatus_transporte(
    codigo_transporte,
    estatus_anterior,
    estatus_nuevo,
    usuario,
    observaciones
):

    db_path = get_db_path("logistica")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    fecha_cambio = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("""
        UPDATE embarques
        SET
            estatus = ?,
            fecha_estatus = ?,
            usuario_estatus = ?,
            observaciones_estatus = ?
        WHERE codigo_transporte = ?
    """, (
        estatus_nuevo,
        fecha_cambio,
        usuario,
        observaciones,
        codigo_transporte
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
        codigo_transporte,
        estatus_anterior,
        estatus_nuevo,
        fecha_cambio,
        usuario,
        observaciones
    ))

    conn.commit()
    conn.close()


# =====================================================
# APP
# =====================================================

def actualizar_estatus_embarque_app():

    st.title("🚚 Actualizar estatus transporte")

    # =====================================================
    # SESSION STATE
    # =====================================================

    if "refresh_estatus_transporte" not in st.session_state:

        st.session_state["refresh_estatus_transporte"] = False

    # =====================================================
    # CONSULTAR TRANSPORTES
    # =====================================================

    try:

        df_transportes = obtener_transportes_para_estatus()

        if st.session_state["refresh_estatus_transporte"]:

            st.session_state["refresh_estatus_transporte"] = False

            df_transportes = obtener_transportes_para_estatus()

    except Exception as e:

        st.error("❌ Error consultando transportes")
        st.exception(e)
        return

    if df_transportes.empty:

        st.warning("No existen transportes activos registrados.")
        return

    try:

        catalogo_estatus = obtener_catalogo_estatus()

    except Exception:

        catalogo_estatus = [
            "En almacén",
            "En patio",
            "Ya salió",
            "En tránsito",
            "Entregado",
            "Cancelado"
        ]

    # =====================================================
    # FILTROS
    # =====================================================

    st.subheader("🔎 Buscar transporte")

    col1, col2, col3 = st.columns(3)

    with col1:

        filtro_transporte = st.text_input("Código transporte")

    with col2:

        filtro_cliente = st.text_input("Cliente")

    with col3:

        filtro_estatus = st.selectbox(
            "Estatus actual",
            ["Todos"] + sorted(
                df_transportes["estatus"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )
        )

    df_filtrado = df_transportes.copy()

    if filtro_transporte:

        df_filtrado = df_filtrado[
            df_filtrado["codigo_transporte"]
            .astype(str)
            .str.contains(filtro_transporte, case=False, na=False)
        ]

    if filtro_cliente:

        df_filtrado = df_filtrado[
            df_filtrado["clientes"]
            .astype(str)
            .str.contains(filtro_cliente, case=False, na=False)
        ]

    if filtro_estatus != "Todos":

        df_filtrado = df_filtrado[
            df_filtrado["estatus"].astype(str) == filtro_estatus
        ]

    if df_filtrado.empty:

        st.warning("No hay transportes con los filtros seleccionados.")
        return

    # =====================================================
    # SELECCIONAR TRANSPORTE
    # =====================================================

    df_filtrado["opcion"] = (
        df_filtrado["codigo_transporte"].astype(str)
        + " | "
        + df_filtrado["clientes"].fillna("").astype(str)
        + " | "
        + df_filtrado["destinos"].fillna("").astype(str)
        + " | "
        + df_filtrado["estatus"].fillna("").astype(str)
    )

    opcion = st.selectbox(
        "Selecciona transporte",
        df_filtrado["opcion"].tolist()
    )

    codigo_transporte = opcion.split(" | ")[0]

    transporte = df_filtrado[
        df_filtrado["codigo_transporte"].astype(str)
        == codigo_transporte
    ].iloc[0]

    st.divider()

    # =====================================================
    # DATOS DEL TRANSPORTE
    # =====================================================

    st.subheader("🚚 Datos del transporte")

    c1, c2, c3 = st.columns(3)

    with c1:

        st.write(
            "**Código transporte:**",
            transporte.get("codigo_transporte", "")
        )

        st.write(
            "**Hoja carga:**",
            transporte.get("folio_hoja_carga", "")
        )

        st.write(
            "**Total embarques:**",
            transporte.get("total_embarques", 0)
        )

    with c2:

        st.write(
            "**Clientes:**",
            transporte.get("clientes", "")
        )

        st.write(
            "**Destinos:**",
            transporte.get("destinos", "")
        )

        st.write(
            "**Ruta:**",
            transporte.get("ruta", "")
        )

    with c3:

        st.write(
            "**Transportista:**",
            transporte.get("transportista", "")
        )

        st.write(
            "**Vehículo:**",
            transporte.get("vehiculo", "")
        )

        st.write(
            "**Placas:**",
            transporte.get("placas", "")
        )

    estatus_actual = str(
        transporte.get("estatus", "") or ""
    )

    st.info(f"📌 Estatus actual: {estatus_actual}")

    # =====================================================
    # NUEVO ESTATUS
    # =====================================================

    st.subheader("🔄 Cambio de estatus")

    if estatus_actual in catalogo_estatus:

        index_estatus = catalogo_estatus.index(
            estatus_actual
        )

    else:

        index_estatus = 0

    nuevo_estatus = st.selectbox(
        "Nuevo estatus",
        catalogo_estatus,
        index=index_estatus
    )

    usuario = st.text_input(
        "Usuario",
        value="admin"
    )

    observaciones = st.text_area(
        "Observaciones del cambio"
    )

    col_btn1, col_btn2 = st.columns([1, 3])

    with col_btn1:

        guardar = st.button(
            "💾 Guardar cambio",
            use_container_width=True
        )

    if guardar:

        if nuevo_estatus == estatus_actual:

            st.warning(
                "Selecciona un estatus diferente al actual."
            )

        else:

            try:

                actualizar_estatus_transporte(
                    codigo_transporte,
                    estatus_actual,
                    nuevo_estatus,
                    usuario,
                    observaciones
                )

                st.session_state[
                    "refresh_estatus_transporte"
                ] = True

                st.success(
                    f"✅ Estatus actualizado: "
                    f"{codigo_transporte} → "
                    f"{nuevo_estatus}"
                )

                st.rerun()

            except Exception as e:

                st.error("❌ Error actualizando estatus")
                st.exception(e)

    # =====================================================
    # DETALLE TRANSPORTE
    # =====================================================

    st.divider()

    tab1, tab2 = st.tabs([
        "📄 Carga del transporte",
        "🕒 Historial de estatus"
    ])

    with tab1:

        try:

            df_detalle = obtener_detalle_transporte(
                codigo_transporte
            )

            if df_detalle.empty:

                st.warning(
                    "Este transporte no tiene detalle registrado."
                )

            else:

                st.dataframe(
                    df_detalle,
                    use_container_width=True,
                    height=300,
                    hide_index=True
                )

        except Exception as e:

            st.error(
                "❌ Error consultando carga del transporte"
            )

            st.exception(e)

    with tab2:

        try:

            df_historial = obtener_historial_estatus(
                codigo_transporte
            )

            if df_historial.empty:

                st.info(
                    "Este transporte todavía no tiene historial."
                )

            else:

                st.dataframe(
                    df_historial,
                    use_container_width=True,
                    height=300,
                    hide_index=True
                )

        except Exception as e:

            st.error("❌ Error consultando historial")
            st.exception(e)
