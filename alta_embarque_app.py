
import streamlit as st
import sqlite3
import pandas as pd

from datetime import date, datetime

from sigem_db import get_db_path


def cargar_pedidos_excel(archivo_excel):

    pedidos_df = pd.read_excel(
        archivo_excel,
        sheet_name="pedidos"
    )

    detalle_df = pd.read_excel(
        archivo_excel,
        sheet_name="detalle_pedido"
    )

    return pedidos_df, detalle_df


def guardar_pedidos_excel(pedidos_df, detalle_df):

    conn = sqlite3.connect(get_db_path("logistica"))
    cur = conn.cursor()

    for _, row in pedidos_df.iterrows():

        cur.execute("""
            INSERT OR REPLACE INTO pedidos (
                pedido,
                fecha,
                cliente,
                destino,
                estatus,
                observaciones,
                usuario,
                fecha_creacion
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row.get("pedido", ""),
            str(row.get("fecha", "")),
            row.get("cliente", ""),
            row.get("destino", ""),
            row.get("estatus", "Pendiente"),
            row.get("observaciones", ""),
            row.get("usuario", "admin"),
            datetime.now()
        ))

    for _, row in detalle_df.iterrows():

        cur.execute("""
            INSERT INTO detalle_pedido (
                pedido,
                codigo_material,
                descripcion,
                cantidad_pedida,
                peso,
                volumen,
                bodega,
                ubicacion
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row.get("pedido", ""),
            row.get("codigo_material", ""),
            row.get("descripcion", ""),
            row.get("cantidad_pedida", 0),
            row.get("peso", 0),
            row.get("volumen", 0),
            row.get("bodega", ""),
            row.get("ubicacion", "")
        ))

    conn.commit()
    conn.close()


def obtener_pedidos():

    conn = sqlite3.connect(get_db_path("logistica"))

    df = pd.read_sql_query("""
        SELECT
            pedido,
            fecha,
            cliente,
            destino,
            estatus
        FROM pedidos
        ORDER BY pedido
    """, conn)

    conn.close()

    return df


def obtener_detalle_pedido(pedido):

    conn = sqlite3.connect(get_db_path("logistica"))

    df = pd.read_sql_query("""
        SELECT
            pedido,
            codigo_material,
            descripcion,
            cantidad_pedida,
            peso,
            volumen,
            bodega,
            ubicacion
        FROM detalle_pedido
        WHERE pedido = ?
        ORDER BY codigo_material
    """, conn, params=[pedido])

    conn.close()

    return df


def guardar_embarque(
    folio_embarque,
    pedido,
    fecha,
    cliente,
    destino,
    transportista,
    vehiculo,
    operador,
    ruta,
    estatus,
    observaciones,
    usuario,
    detalle_df
):

    conn = sqlite3.connect(get_db_path("logistica"))
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO embarques (
            folio_embarque,
            fecha,
            pedido,
            cliente,
            destino,
            transportista,
            vehiculo,
            operador,
            ruta,
            estatus,
            observaciones,
            usuario,
            fecha_creacion
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        folio_embarque,
        fecha,
        pedido,
        cliente,
        destino,
        transportista,
        vehiculo,
        operador,
        ruta,
        estatus,
        observaciones,
        usuario,
        datetime.now()
    ))

    for _, row in detalle_df.iterrows():

        cur.execute("""
            INSERT INTO detalle_embarque (
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
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            folio_embarque,
            pedido,
            row.get("codigo_material", ""),
            row.get("descripcion", ""),
            row.get("cantidad_pedida", 0),
            row.get("cantidad_pedida", 0),
            row.get("peso", 0),
            row.get("volumen", 0),
            row.get("bodega", ""),
            row.get("ubicacion", "")
        ))

    conn.commit()
    conn.close()


def alta_embarque_app():

    st.title("➕ Alta embarque")

    st.caption("Pedido → Detalle pedido → Embarque → Detalle embarque")

    st.divider()

    st.subheader("📤 Cargar pedido desde Excel")

    archivo_excel = st.file_uploader(
        "Subir archivo Excel con hojas: pedidos y detalle_pedido",
        type=["xlsx"]
    )

    if archivo_excel is not None:

        try:
            pedidos_df, detalle_excel_df = cargar_pedidos_excel(archivo_excel)

            st.write("📄 Pedidos")
            st.dataframe(
                pedidos_df,
                use_container_width=True,
                hide_index=True
            )

            st.write("📦 Detalle pedido")
            st.dataframe(
                detalle_excel_df,
                use_container_width=True,
                hide_index=True
            )

            if st.button("💾 Guardar pedido en logística", use_container_width=True):
                guardar_pedidos_excel(pedidos_df, detalle_excel_df)
                st.success("✅ Pedido cargado correctamente en logistica.db")

        except Exception as e:
            st.error("❌ Error leyendo o guardando Excel.")
            st.exception(e)

    st.divider()

    st.subheader("🚚 Generar embarque desde pedido")

    pedidos_df = obtener_pedidos()

    if pedidos_df.empty:
        st.warning("No hay pedidos cargados. Primero sube un Excel de pedido.")
        return

    lista_pedidos = ["Selecciona pedido"] + pedidos_df["pedido"].tolist()

    pedido_seleccionado = st.selectbox(
        "📄 Pedido origen",
        lista_pedidos
    )

    if pedido_seleccionado == "Selecciona pedido":
        st.info("Selecciona un pedido para continuar.")
        return

    pedido_row = pedidos_df[pedidos_df["pedido"] == pedido_seleccionado].iloc[0]

    cliente = pedido_row["cliente"]
    destino = pedido_row["destino"]

    detalle_df = obtener_detalle_pedido(pedido_seleccionado)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Pedido", pedido_seleccionado)

    with c2:
        st.metric("Cliente", cliente)

    with c3:
        st.metric("Destino", destino)

    st.subheader("📦 Detalle del pedido")

    st.dataframe(
        detalle_df,
        use_container_width=True,
        hide_index=True
    )

    with st.form("form_alta_embarque"):

        st.subheader("🚚 Datos del embarque")

        col1, col2 = st.columns(2)

        with col1:
            folio_embarque = st.text_input("Folio embarque")
            fecha_embarque = st.date_input("Fecha embarque", value=date.today())
            transportista = st.text_input("Transportista")
            vehiculo = st.text_input("Vehículo")

        with col2:
            operador = st.text_input("Operador")
            ruta = st.text_input("Ruta")
            estatus = st.selectbox(
                "Estatus",
                [
                    "Pendiente",
                    "Preparación",
                    "En ruta",
                    "Entregado",
                    "Cancelado"
                ]
            )
            usuario = st.text_input("Usuario", value="admin")

        observaciones = st.text_area("Observaciones")

        guardar = st.form_submit_button("💾 Guardar embarque")

    if guardar:

        if not folio_embarque:
            st.warning("Captura el folio del embarque.")
            return

        try:
            guardar_embarque(
                folio_embarque,
                pedido_seleccionado,
                fecha_embarque,
                cliente,
                destino,
                transportista,
                vehiculo,
                operador,
                ruta,
                estatus,
                observaciones,
                usuario,
                detalle_df
            )

            st.success("✅ Embarque generado correctamente desde el pedido.")

        except sqlite3.IntegrityError:
            st.error("❌ Ese folio de embarque ya existe.")

        except Exception as e:
            st.error("❌ Error guardando embarque.")
            st.exception(e)
