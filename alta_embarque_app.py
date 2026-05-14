
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

from sigem_db import get_db_path


# =====================================================
# OBTENER HOJAS CARGA PENDIENTES
# =====================================================

def obtener_hojas_carga_pendientes():

    conn = sqlite3.connect(
        get_db_path("logistica")
    )

    query = """
        SELECT
            folio_hoja_carga,
            cliente,
            destino,
            COUNT(codigo_material) AS materiales,
            ROUND(SUM(peso), 2) AS peso_total,
            ROUND(SUM(volumen), 2) AS volumen_total

        FROM detalle_embarque

        WHERE folio_embarque IS NULL
           OR folio_embarque = ''

        GROUP BY
            folio_hoja_carga,
            cliente,
            destino

        ORDER BY folio_hoja_carga DESC
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


# =====================================================
# OBTENER TRANSPORTES
# =====================================================

def obtener_transportes():

    conn = sqlite3.connect(
        get_db_path("logistica")
    )

    query = """
        SELECT
            codigo_transporte,
            transportista,
            vehiculo,
            placas,
            operador,
            capacidad_peso,
            capacidad_volumen,
            estatus

        FROM transportes

        ORDER BY codigo_transporte
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


# =====================================================
# GENERAR FOLIO EMBARQUE
# =====================================================

def generar_folio_embarque():

    fecha = datetime.now().strftime("%Y%m%d%H%M%S")

    return f"EMB-{fecha}"


# =====================================================
# APP
# =====================================================

def alta_embarque_app():

    st.title("🚛 Planeación de embarque")

    st.caption(
        "Hoja carga → Transporte → Embarque"
    )

    st.divider()

    # =====================================================
    # CARGAR INFORMACION
    # =====================================================

    try:

        df_hojas = obtener_hojas_carga_pendientes()

        df_transportes = obtener_transportes()

    except Exception as e:

        st.error("❌ Error cargando información.")
        st.exception(e)

        return

    if df_hojas.empty:

        st.warning(
            "No existen hojas de carga pendientes."
        )

        return

    if df_transportes.empty:

        st.warning(
            "No existen transportes registrados."
        )

        return

    # =====================================================
    # KPIS
    # =====================================================

    total_hojas = len(df_hojas)

    peso_total = round(
        df_hojas["peso_total"].sum(),
        2
    )

    volumen_total = round(
        df_hojas["volumen_total"].sum(),
        2
    )

    total_transportes = len(df_transportes)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "📦 Hojas pendientes",
        total_hojas
    )

    c2.metric(
        "⚖️ Peso total",
        peso_total
    )

    c3.metric(
        "📐 Volumen total",
        volumen_total
    )

    c4.metric(
        "🚛 Transportes",
        total_transportes
    )

    st.divider()

    # =====================================================
    # PANTALLA PRINCIPAL
    # =====================================================

    col1, col2, col3 = st.columns([4, 3, 4])

    # =====================================================
    # PANEL 1
    # =====================================================

    with col1:

        st.subheader("📦 Hojas carga pendientes")

        hoja_seleccionada = st.selectbox(
            "Selecciona hoja carga",
            df_hojas["folio_hoja_carga"]
            .astype(str)
            .tolist()
        )

        hoja = df_hojas[
            df_hojas["folio_hoja_carga"]
            .astype(str)
            == str(hoja_seleccionada)
        ].iloc[0]

        st.markdown("---")

        st.write(
            f"**Cliente:** {hoja['cliente']}"
        )

        st.write(
            f"**Destino:** {hoja['destino']}"
        )

        st.write(
            f"**Materiales:** {hoja['materiales']}"
        )

        st.write(
            f"**Peso total:** {hoja['peso_total']}"
        )

        st.write(
            f"**Volumen total:** {hoja['volumen_total']}"
        )

    # =====================================================
    # PANEL 2
    # =====================================================

    with col2:

        st.subheader("🚛 Transportes")

        transporte_seleccionado = st.selectbox(
            "Selecciona transporte",
            df_transportes["codigo_transporte"]
            .astype(str)
            .tolist()
        )

        transporte = df_transportes[
            df_transportes["codigo_transporte"]
            .astype(str)
            == str(transporte_seleccionado)
        ].iloc[0]

        st.markdown("---")

        st.write(
            f"**Transportista:** {transporte['transportista']}"
        )

        st.write(
            f"**Vehículo:** {transporte['vehiculo']}"
        )

        st.write(
            f"**Operador:** {transporte['operador']}"
        )

        st.write(
            f"**Cap. peso:** {transporte['capacidad_peso']}"
        )

        st.write(
            f"**Cap. volumen:** {transporte['capacidad_volumen']}"
        )

        st.write(
            f"**Estatus:** {transporte['estatus']}"
        )

    # =====================================================
    # PANEL 3
    # =====================================================

    with col3:

        st.subheader("✅ Embarque a crear")

        peso_hoja = float(
            hoja["peso_total"]
        )

        volumen_hoja = float(
            hoja["volumen_total"]
        )

        capacidad_peso = float(
            transporte["capacidad_peso"]
        )

        capacidad_volumen = float(
            transporte["capacidad_volumen"]
        )

        porcentaje_peso = round(
            (peso_hoja / capacidad_peso) * 100,
            1
        ) if capacidad_peso > 0 else 0

        porcentaje_volumen = round(
            (volumen_hoja / capacidad_volumen) * 100,
            1
        ) if capacidad_volumen > 0 else 0

        st.write(
            f"**Hoja carga:** {hoja_seleccionada}"
        )

        st.write(
            f"**Transporte:** {transporte_seleccionado}"
        )

        st.write(
            f"**Peso hoja:** {peso_hoja}"
        )

        st.write(
            f"**Volumen hoja:** {volumen_hoja}"
        )

        st.write(
            f"**% ocupación peso:** {porcentaje_peso}%"
        )

        st.write(
            f"**% ocupación volumen:** {porcentaje_volumen}%"
        )

        st.markdown("---")

        validacion_ok = True

        if peso_hoja > capacidad_peso:

            st.error(
                "❌ El peso excede la capacidad del transporte."
            )

            validacion_ok = False

        if volumen_hoja > capacidad_volumen:

            st.error(
                "❌ El volumen excede la capacidad del transporte."
            )

            validacion_ok = False

        if validacion_ok:

            st.success(
                "✅ Transporte válido para la carga."
            )

        st.markdown("---")

        if st.button(
            "🚀 Crear embarque",
            use_container_width=True,
            disabled=not validacion_ok
        ):

            try:

                folio_embarque = generar_folio_embarque()

                st.success(
                    f"✅ Embarque creado: {folio_embarque}"
                )

                st.info(
                    "Próximo paso: guardar encabezado y detalle."
                )

            except Exception as e:

                st.error(
                    "❌ Error creando embarque."
                )

                st.exception(e)
