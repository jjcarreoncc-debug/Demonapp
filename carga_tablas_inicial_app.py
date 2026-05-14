import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

from sigem_db import get_db_path

st.warning("NUEVO ARCHIVO ALTA EMBARQUE - SELECCIÓN MULTIPLE")


# =====================================================
# UTILIDADES
# =====================================================

def obtener_columnas_tabla(conn, tabla):

    df_cols = pd.read_sql_query(
        f"PRAGMA table_info({tabla})",
        conn
    )

    return df_cols["name"].tolist()


def insertar_dinamico(conn, tabla, datos):

    columnas_tabla = obtener_columnas_tabla(
        conn,
        tabla
    )

    datos_filtrados = {
        k: v
        for k, v in datos.items()
        if k in columnas_tabla
    }

    if not datos_filtrados:
        return

    columnas = list(datos_filtrados.keys())

    placeholders = ",".join(["?"] * len(columnas))

    sql = f"""
        INSERT INTO {tabla} (
            {",".join(columnas)}
        )
        VALUES (
            {placeholders}
        )
    """

    valores = [
        datos_filtrados[col]
        for col in columnas
    ]

    conn.execute(
        sql,
        valores
    )


# =====================================================
# OBTENER HOJAS CARGA PENDIENTES
# =====================================================

def obtener_hojas_carga_pendientes():

    conn = sqlite3.connect(
        get_db_path("logistica")
    )

    inventarios_db = get_db_path("inventarios")

    conn.execute(
        f"ATTACH DATABASE '{inventarios_db}' AS inv"
    )

    query = """
        SELECT
            h.folio_hoja_carga,
            h.pedido,
            h.cliente,
            h.destino,
            h.estatus,
            COUNT(d.codigo_material) AS materiales,
            ROUND(COALESCE(SUM(d.peso), 0), 2) AS peso_total,
            ROUND(COALESCE(SUM(d.volumen), 0), 2) AS volumen_total

        FROM inv.hoja_carga h

        LEFT JOIN inv.detalle_hoja_carga d
            ON h.folio_hoja_carga = d.folio_hoja_carga

        WHERE h.folio_hoja_carga NOT IN (
            SELECT folio_hoja_carga
            FROM embarques
            WHERE folio_hoja_carga IS NOT NULL
              AND TRIM(folio_hoja_carga) <> ''
        )

        GROUP BY
            h.folio_hoja_carga,
            h.pedido,
            h.cliente,
            h.destino,
            h.estatus

        ORDER BY h.folio_hoja_carga DESC
    """

    df = pd.read_sql_query(
        query,
        conn
    )

    conn.close()

    return df


# =====================================================
# OBTENER DETALLE HOJA CARGA
# =====================================================

def obtener_detalle_hoja_carga(folio_hoja_carga):

    conn = sqlite3.connect(
        get_db_path("inventarios")
    )

    query = """
        SELECT
            folio_hoja_carga,
            pedido,
            codigo_material,
            descripcion,
            cantidad_pedido,
            cantidad_surtida,
            bodega,
            ubicacion,
            peso,
            volumen,
            observaciones

        FROM detalle_hoja_carga

        WHERE folio_hoja_carga = ?
    """

    df = pd.read_sql_query(
        query,
        conn,
        params=[folio_hoja_carga]
    )

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
            descripcion,
            transportista,
            vehiculo,
            placas,
            operador,
            codigo_ruta,
            capacidad_peso,
            capacidad_volumen,
            estatus

        FROM transportes

        WHERE estatus IS NULL
           OR estatus = ''
           OR estatus = 'Disponible'

        ORDER BY codigo_transporte
    """

    df = pd.read_sql_query(
        query,
        conn
    )

    conn.close()

    return df


# =====================================================
# GENERAR FOLIO EMBARQUE
# =====================================================

def generar_folio_embarque():

    fecha = datetime.now().strftime("%Y%m%d%H%M%S")

    return f"EMB-{fecha}"


# =====================================================
# CREAR EMBARQUES
# =====================================================

def crear_embarques_desde_hojas(df_seleccionadas, transporte):

    conn = sqlite3.connect(
        get_db_path("logistica")
    )

    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    folios_creados = []

    try:

        for i, hoja in df_seleccionadas.iterrows():

            folio_embarque = generar_folio_embarque() + f"-{i + 1}"

            datos_embarque = {
                "folio_embarque": folio_embarque,
                "folio_hoja_carga": hoja["folio_hoja_carga"],
                "folio_ruta": transporte.get("codigo_ruta", ""),
                "codigo_ruta": transporte.get("codigo_ruta", ""),
                "codigo_transporte": transporte.get("codigo_transporte", ""),
                "pedido": hoja.get("pedido", ""),
                "fecha": fecha_actual,
                "cliente": hoja.get("cliente", ""),
                "destino": hoja.get("destino", ""),
                "transportista": transporte.get("transportista", ""),
                "vehiculo": transporte.get("vehiculo", ""),
                "placas": transporte.get("placas", ""),
                "operador": transporte.get("operador", ""),
                "ruta": transporte.get("codigo_ruta", ""),
                "estatus": "En almacén",
                "fecha_estatus": fecha_actual,
                "usuario_estatus": "admin",
                "observaciones": "Creado desde asignación de transporte",
                "usuario": "admin",
                "fecha_creacion": fecha_actual
            }

            insertar_dinamico(
                conn,
                "embarques",
                datos_embarque
            )

            df_detalle = obtener_detalle_hoja_carga(
                hoja["folio_hoja_carga"]
            )

            for _, det in df_detalle.iterrows():

                datos_detalle = {
                    "folio_embarque": folio_embarque,
                    "folio_hoja_carga": hoja["folio_hoja_carga"],
                    "folio_ruta": transporte.get("codigo_ruta", ""),
                    "pedido": det.get("pedido", hoja.get("pedido", "")),
                    "codigo_material": det.get("codigo_material", ""),
                    "descripcion": det.get("descripcion", ""),
                    "cantidad_pedida": det.get("cantidad_pedido", 0),
                    "cantidad_embarcar": det.get("cantidad_surtida", det.get("cantidad_pedido", 0)),
                    "peso": det.get("peso", 0),
                    "volumen": det.get("volumen", 0),
                    "bodega": det.get("bodega", ""),
                    "ubicacion": det.get("ubicacion", "")
                }

                insertar_dinamico(
                    conn,
                    "detalle_embarque",
                    datos_detalle
                )

            folios_creados.append(
                folio_embarque
            )

        conn.commit()

    except Exception as e:

        conn.rollback()
        conn.close()
        raise e

    conn.close()

    return folios_creados


# =====================================================
# APP
# =====================================================

def alta_embarque_app():

    st.title("🚛 Asignación de embarques a transporte")

    st.caption(
        "Selecciona hojas de carga pendientes y asígnalas a un transporte disponible."
    )

    st.divider()

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
            "No existen transportes disponibles."
        )

        return

    df_hojas["seleccionar"] = False

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

    c1.metric("📦 Hojas pendientes", total_hojas)
    c2.metric("⚖️ Peso total", peso_total)
    c3.metric("📐 Volumen total", volumen_total)
    c4.metric("🚛 Transportes", total_transportes)

    st.divider()

    col1, col2, col3 = st.columns([5, 3, 4])

    with col1:

        st.subheader("📦 Hojas de carga pendientes")

        columnas_mostrar = [
            "seleccionar",
            "folio_hoja_carga",
            "cliente",
            "destino",
            "materiales",
            "peso_total",
            "volumen_total",
            "estatus"
        ]

        df_editor = st.data_editor(
            df_hojas[columnas_mostrar],
            hide_index=True,
            use_container_width=True,
            column_config={
                "seleccionar": st.column_config.CheckboxColumn(
                    "Sel.",
                    default=False
                ),
                "folio_hoja_carga": "Hoja",
                "cliente": "Cliente",
                "destino": "Destino",
                "materiales": "Mat.",
                "peso_total": "Peso",
                "volumen_total": "Vol.",
                "estatus": "Estatus"
            },
            disabled=[
                "folio_hoja_carga",
                "cliente",
                "destino",
                "materiales",
                "peso_total",
                "volumen_total",
                "estatus"
            ],
            key="editor_hojas_carga"
        )

        df_seleccionadas = df_editor[
            df_editor["seleccionar"] == True
        ]

        st.caption(
            f"Hojas seleccionadas: {len(df_seleccionadas)}"
        )

    with col2:

        st.subheader("🚛 Transporte")

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

        st.write(f"**Transportista:** {transporte['transportista']}")
        st.write(f"**Vehículo:** {transporte['vehiculo']}")
        st.write(f"**Placas:** {transporte['placas']}")
        st.write(f"**Operador:** {transporte['operador']}")
        st.write(f"**Ruta:** {transporte.get('codigo_ruta', '')}")
        st.write(f"**Cap. peso:** {transporte['capacidad_peso']}")
        st.write(f"**Cap. volumen:** {transporte['capacidad_volumen']}")

    with col3:

        st.subheader("✅ Carga planeada")

        peso_seleccionado = round(
            df_seleccionadas["peso_total"].sum(),
            2
        ) if not df_seleccionadas.empty else 0

        volumen_seleccionado = round(
            df_seleccionadas["volumen_total"].sum(),
            2
        ) if not df_seleccionadas.empty else 0

        capacidad_peso = float(
            transporte["capacidad_peso"]
        )

        capacidad_volumen = float(
            transporte["capacidad_volumen"]
        )

        porcentaje_peso = round(
            (peso_seleccionado / capacidad_peso) * 100,
            1
        ) if capacidad_peso > 0 else 0

        porcentaje_volumen = round(
            (volumen_seleccionado / capacidad_volumen) * 100,
            1
        ) if capacidad_volumen > 0 else 0

        st.metric("📦 Hojas seleccionadas", len(df_seleccionadas))
        st.metric("⚖️ Peso seleccionado", peso_seleccionado)
        st.metric("📐 Volumen seleccionado", volumen_seleccionado)

        st.markdown("---")

        st.write(f"**Capacidad peso:** {capacidad_peso}")
        st.write(f"**Capacidad volumen:** {capacidad_volumen}")
        st.write(f"**% ocupación peso:** {porcentaje_peso}%")
        st.write(f"**% ocupación volumen:** {porcentaje_volumen}%")

        st.markdown("---")

        validacion_ok = True

        if df_seleccionadas.empty:

            st.warning(
                "Selecciona una o más hojas de carga."
            )

            validacion_ok = False

        if peso_seleccionado > capacidad_peso:

            st.error(
                "❌ El peso excede la capacidad del transporte."
            )

            validacion_ok = False

        if volumen_seleccionado > capacidad_volumen:

            st.error(
                "❌ El volumen excede la capacidad del transporte."
            )

            validacion_ok = False

        if validacion_ok:

            st.success(
                "✅ Transporte válido para la carga seleccionada."
            )

        if st.button(
            "🚀 Confirmar asignación",
            use_container_width=True,
            disabled=not validacion_ok
        ):

            try:

                folios = crear_embarques_desde_hojas(
                    df_seleccionadas,
                    transporte
                )

                st.success(
                    "✅ Embarques creados correctamente"
                )

                st.write("Folios generados:")

                st.write(folios)

            except Exception as e:

                st.error(
                    "❌ Error creando embarques."
                )

                st.exception(e)


if __name__ == "__main__":

    alta_embarque_app()
