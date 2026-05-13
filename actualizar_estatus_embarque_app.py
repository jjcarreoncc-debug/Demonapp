
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

from sigem_db import get_db_path


# =====================================================
# OBTENER EMBARQUES
# =====================================================

def obtener_embarques_para_estatus():

    db_path = get_db_path("logistica")

    conn = sqlite3.connect(db_path)

    query = """
        SELECT
            folio_embarque,
            folio_hoja_carga,
            folio_ruta,
            pedido,
            fecha,
            cliente,
            destino,
            transportista,
            vehiculo,
            placas,
            operador,
            ruta,
            estatus,
            fecha_estatus,
            usuario_estatus,
            observaciones_estatus
        FROM embarques
        ORDER BY fecha DESC, folio_embarque DESC
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
# OBTENER DETALLE EMBARQUE
# =====================================================

def obtener_detalle_embarque(folio_embarque):

    db_path = get_db_path("logistica")

    conn = sqlite3.connect(db_path)

    query = """
        SELECT
            folio_embarque,
            folio_hoja_carga,
            folio_ruta,
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
        WHERE folio_embarque = ?
    """

    df = pd.read_sql_query(
        query,
        conn,
        params=[folio_embarque]
    )

    conn.close()

    return df


# =====================================================
# OBTENER HISTORIAL
# =====================================================

def obtener_historial_estatus(folio_embarque):

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
        params=[folio_embarque]
    )

    conn.close()

    return df


# =====================================================
# ACTUALIZAR ESTATUS
# =====================================================

def actualizar_estatus_embarque(
    folio_embarque,
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
        WHERE folio_embarque = ?
    """, (
        estatus_nuevo,
        fecha_cambio,
        usuario,
        observaciones,
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

    st.title("✏️ Actualizar estatus embarque")

    try:

        df_embarques = obtener_embarques_para_estatus()

    except Exception as e:

        st.error("❌ Error consultando embarques")
        st.exception(e)
        return

    if df_embarques.empty:

        st.warning("No existen embarques registrados.")
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

    st.subheader("🔎 Buscar embarque")

    col1, col2, col3 = st.columns(3)

    with col1:

        filtro_folio = st.text_input("Folio embarque")

    with col2:

        filtro_cliente = st.text_input("Cliente")

    with col3:

        filtro_estatus = st.selectbox(
            "Estatus actual",
            ["Todos"] + sorted(
                df_embarques["estatus"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )
        )

    df_filtrado = df_embarques.copy()

    if filtro_folio:

        df_filtrado = df_filtrado[
            df_filtrado["folio_embarque"]
            .astype(str)
            .str.contains(filtro_folio, case=False, na=False)
        ]

    if filtro_cliente:

        df_filtrado = df_filtrado[
            df_filtrado["cliente"]
            .astype(str)
            .str.contains(filtro_cliente, case=False, na=False)
        ]

    if filtro_estatus != "Todos":

        df_filtrado = df_filtrado[
            df_filtrado["estatus"].astype(str) == filtro_estatus
        ]

    if df_filtrado.empty:

        st.warning("No hay embarques con los filtros seleccionados.")
        return

    # =====================================================
    # SELECCIONAR EMBARQUE
    # =====================================================

    df_filtrado["opcion"] = (
        df_filtrado["folio_embarque"].astype(str)
        + " | "
        + df_filtrado["cliente"].fillna("").astype(str)
        + " | "
        + df_filtrado["destino"].fillna("").astype(str)
        + " | "
        + df_filtrado["estatus"].fillna("").astype(str)
    )

    opcion = st.selectbox(
        "Selecciona embarque",
        df_filtrado["opcion"].tolist()
    )

    folio_seleccionado = opcion.split(" | ")[0]

    embarque = df_filtrado[
        df_filtrado["folio_embarque"].astype(str) == folio_seleccionado
    ].iloc[0]

    st.divider()

    # =====================================================
    # DATOS DEL EMBARQUE
    # =====================================================

    st.subheader("📦 Datos del embarque")

    c1, c2, c3 = st.columns(3)

    with c1:

        st.write("**Folio embarque:**", embarque.get("folio_embarque", ""))
        st.write("**Hoja carga:**", embarque.get("folio_hoja_carga", ""))
        st.write("**Pedido:**", embarque.get("pedido", ""))

    with c2:

        st.write("**Cliente:**", embarque.get("cliente", ""))
        st.write("**Destino:**", embarque.get("destino", ""))
        st.write("**Ruta:**", embarque.get("ruta", ""))

    with c3:

        st.write("**Transportista:**", embarque.get("transportista", ""))
        st.write("**Vehículo:**", embarque.get("vehiculo", ""))
        st.write("**Placas:**", embarque.get("placas", ""))

    estatus_actual = str(embarque.get("estatus", "") or "")

    st.info(f"📌 Estatus actual: {estatus_actual}")

    # =====================================================
    # NUEVO ESTATUS
    # =====================================================

    st.subheader("🔄 Cambio de estatus")

    if estatus_actual in catalogo_estatus:

        index_estatus = catalogo_estatus.index(estatus_actual)

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

            st.warning("Selecciona un estatus diferente al actual.")

        else:

            try:

                actualizar_estatus_embarque(
                    folio_seleccionado,
                    estatus_actual,
                    nuevo_estatus,
                    usuario,
                    observaciones
                )

                st.success(
                    f"✅ Estatus actualizado: {folio_seleccionado} → {nuevo_estatus}"
                )

                st.rerun()

            except Exception as e:

                st.error("❌ Error actualizando estatus")
                st.exception(e)

    # =====================================================
    # CARGA DEL EMBARQUE
    # =====================================================

    st.divider()

    tab1, tab2 = st.tabs([
        "📄 Carga del embarque",
        "🕒 Historial de estatus"
    ])

    with tab1:

        try:

            df_detalle = obtener_detalle_embarque(
                folio_seleccionado
            )

            if df_detalle.empty:

                st.warning("Este embarque no tiene detalle registrado.")

            else:

                st.dataframe(
                    df_detalle,
                    use_container_width=True,
                    height=300,
                    hide_index=True
                )

        except Exception as e:

            st.error("❌ Error consultando carga del embarque")
            st.exception(e)

    with tab2:

        try:

            df_historial = obtener_historial_estatus(
                folio_seleccionado
            )

            if df_historial.empty:

                st.info("Este embarque todavía no tiene historial de cambios.")

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
