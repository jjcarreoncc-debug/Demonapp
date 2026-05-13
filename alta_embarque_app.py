
import streamlit as st
import sqlite3
from datetime import date, datetime

from sigem_db import get_db_path


def alta_embarque_app():

    st.title("➕ Alta embarque")

    st.divider()

    with st.form("form_alta_embarque"):

        st.subheader("📦 Datos generales")

        col1, col2 = st.columns(2)

        with col1:
            folio_embarque = st.text_input("Folio embarque")
            fecha = st.date_input("Fecha", value=date.today())
            pedido = st.text_input("Pedido")
            cliente = st.text_input("Cliente")

        with col2:
            destino = st.text_input("Destino")
            estatus = st.selectbox(
                "Estatus",
                ["Pendiente", "Preparación", "En ruta", "Entregado", "Cancelado"]
            )
            usuario = st.text_input("Usuario", value="admin")

        st.subheader("🚛 Transporte")

        col3, col4 = st.columns(2)

        with col3:
            transportista = st.text_input("Transportista")
            vehiculo = st.text_input("Vehículo")

        with col4:
            operador = st.text_input("Operador")
            ruta = st.text_input("Ruta")

        st.subheader("📦 Datos operativos")

        col5, col6, col7 = st.columns(3)

        with col5:
            peso_total = st.number_input("Peso total", min_value=0.0)

        with col6:
            volumen_total = st.number_input("Volumen total", min_value=0.0)

        with col7:
            cantidad_bultos = st.number_input("Cantidad bultos", min_value=0, step=1)

        observaciones = st.text_area("Observaciones")

        guardar = st.form_submit_button("💾 Guardar embarque")

    if guardar:

        if not folio_embarque:
            st.warning("Captura el folio del embarque.")
            return

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
                peso_total,
                volumen_total,
                cantidad_bultos,
                estatus,
                observaciones,
                usuario,
                fecha_creacion
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            peso_total,
            volumen_total,
            cantidad_bultos,
            estatus,
            observaciones,
            usuario,
            datetime.now()
        ))

        conn.commit()
        conn.close()

        st.success("✅ Embarque registrado correctamente.")
