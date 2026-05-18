
import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import math
from embarques_service import procesar_confirmacion_embarque

from datetime import datetime

from sigem_db import get_db_path

st.set_page_config(
    layout="wide"
)


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

    query = """
        SELECT

            h.folio_hoja_carga,

            h.pedido,

            h.cliente,

            h.destino,

            h.estatus_hoja AS estatus,

            COUNT(d.codigo_material) AS materiales,

            ROUND(COALESCE(SUM(d.peso_calculado), 0), 2) AS peso_total,

            ROUND(COALESCE(SUM(d.volumen_calculado), 0), 2) AS volumen_total

        FROM hojas_carga h

        LEFT JOIN detalle_hoja_carga d
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

            h.estatus_hoja

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
        get_db_path("logistica")
    )

    query = """
        SELECT

            folio_hoja_carga,

            pedido,

            codigo_material,

            descripcion,

            cantidad_reservada AS cantidad_pedido,

            cantidad_reservada AS cantidad_surtida,

            '' AS bodega,

            '' AS ubicacion,

            peso_calculado AS peso,

            volumen_calculado AS volumen,

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
           OR TRIM(estatus) = ''
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

    fecha_actual = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    folios_creados = []

    try:

        for i, hoja in df_seleccionadas.iterrows():

            folio_embarque = (
                generar_folio_embarque()
                + f"-{i + 1}"
            )

            datos_embarque = {

                "folio_embarque": folio_embarque,

                "folio_hoja_carga": hoja["folio_hoja_carga"],

                "folio_ruta": transporte.get(
                    "codigo_ruta",
                    ""
                ),

                "codigo_ruta": transporte.get(
                    "codigo_ruta",
                    ""
                ),

                "codigo_transporte": transporte.get(
                    "codigo_transporte",
                    ""
                ),

                "pedido": hoja.get(
                    "pedido",
                    ""
                ),

                "fecha": fecha_actual,

                "cliente": hoja.get(
                    "cliente",
                    ""
                ),

                "destino": hoja.get(
                    "destino",
                    ""
                ),

                "transportista": transporte.get(
                    "transportista",
                    ""
                ),

                "vehiculo": transporte.get(
                    "vehiculo",
                    ""
                ),

                "placas": transporte.get(
                    "placas",
                    ""
                ),

                "operador": transporte.get(
                    "operador",
                    ""
                ),

                "ruta": transporte.get(
                    "codigo_ruta",
                    ""
                ),

                "estatus": "En almacén",

                "fecha_estatus": fecha_actual,

                "usuario_estatus": "admin",

                "observaciones": (
                    "Creado desde asignación de transporte"
                ),

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

                    "folio_hoja_carga": hoja[
                        "folio_hoja_carga"
                    ],

                    "folio_ruta": transporte.get(
                        "codigo_ruta",
                        ""
                    ),

                    "pedido": det.get(
                        "pedido",
                        hoja.get("pedido", "")
                    ),

                    "codigo_material": det.get(
                        "codigo_material",
                        ""
                    ),

                    "descripcion": det.get(
                        "descripcion",
                        ""
                    ),

                    "cantidad_pedida": det.get(
                        "cantidad_pedido",
                        0
                    ),

                    "cantidad_embarcar": det.get(
                        "cantidad_surtida",
                        det.get(
                            "cantidad_pedido",
                            0
                        )
                    ),

                    "peso": det.get(
                        "peso",
                        0
                    ),

                    "volumen": det.get(
                        "volumen",
                        0
                    ),

                    "bodega": det.get(
                        "bodega",
                        ""
                    ),

                    "ubicacion": det.get(
                        "ubicacion",
                        ""
                    )
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
# APLICAR FILTROS SIDEBAR
# =====================================================

def aplicar_filtros_sidebar(df_hojas):

    df_hojas_filtrado = df_hojas.copy()

    if (
        "filtro_folio_hoja_carga" in st.session_state
        and st.session_state.filtro_folio_hoja_carga != "Todos"
    ):

        df_hojas_filtrado = df_hojas_filtrado[
            df_hojas_filtrado["folio_hoja_carga"].astype(str)
            == st.session_state.filtro_folio_hoja_carga
        ]

    if (
        "filtro_cliente" in st.session_state
        and st.session_state.filtro_cliente != "Todos"
    ):

        df_hojas_filtrado = df_hojas_filtrado[
            df_hojas_filtrado["cliente"].astype(str)
            == st.session_state.filtro_cliente
        ]

    if (
        "filtro_destino" in st.session_state
        and st.session_state.filtro_destino != "Todos"
    ):

        df_hojas_filtrado = df_hojas_filtrado[
            df_hojas_filtrado["destino"].astype(str)
            == st.session_state.filtro_destino
        ]

    if (
        "filtro_estatus" in st.session_state
        and st.session_state.filtro_estatus != "Todos"
    ):

        df_hojas_filtrado = df_hojas_filtrado[
            df_hojas_filtrado["estatus"].astype(str)
            == st.session_state.filtro_estatus
        ]

    return df_hojas_filtrado




# =====================================================
# SIMULACION DE CARGA TRANSPORTE
# =====================================================

def agregar_caja_3d(fig, x0, x1, y0, y1, z0, z1, color, opacity, nombre):

    fig.add_trace(

        go.Mesh3d(

            x=[
                x0, x1, x1, x0,
                x0, x1, x1, x0
            ],

            y=[
                y0, y0, y1, y1,
                y0, y0, y1, y1
            ],

            z=[
                z0, z0, z0, z0,
                z1, z1, z1, z1
            ],

            i=[
                0, 0, 0, 1, 2, 4,
                5, 6, 7, 4, 0, 3
            ],

            j=[
                1, 2, 4, 2, 3, 5,
                6, 7, 4, 7, 3, 7
            ],

            k=[
                2, 3, 5, 5, 7, 6,
                7, 4, 0, 3, 7, 4
            ],

            color=color,

            opacity=opacity,

            flatshading=True,

            name=nombre,

            showscale=False
        )
    )


def obtener_estado_carga(porcentaje_peso, porcentaje_volumen):

    if porcentaje_peso > 100 or porcentaje_volumen > 100:
        return "❌ Excede capacidad", "red"

    if porcentaje_peso >= 90 or porcentaje_volumen >= 90:
        return "⚠️ Cerca del límite", "orange"

    return "✅ Carga válida", "green"


def estimar_tarimas(volumen_total):

    if volumen_total <= 0:
        return 0

    # Estimación operativa inicial:
    # una tarima promedio ocupa entre 2.5 y 3.5 m3
    return max(
        1,
        math.ceil(volumen_total / 3)
    )


def crear_figura_simulacion_carga(
    peso_total,
    volumen_total,
    capacidad_peso,
    capacidad_volumen,
    vehiculo
):

    porcentaje_peso = round(
        (peso_total / capacidad_peso) * 100,
        1
    ) if capacidad_peso > 0 else 0

    porcentaje_volumen = round(
        (volumen_total / capacidad_volumen) * 100,
        1
    ) if capacidad_volumen > 0 else 0

    porcentaje_ocupacion = min(
        max(porcentaje_volumen, porcentaje_peso) / 100,
        1
    )

    tarimas = estimar_tarimas(
        volumen_total
    )

    largo_unidad = 12.0
    ancho_unidad = 2.6
    alto_unidad = 2.8

    largo_ocupado = max(
        largo_unidad * min(porcentaje_volumen / 100, 1),
        0.8 if volumen_total > 0 else 0
    )

    fig = go.Figure()

    # Piso de caja / camion
    agregar_caja_3d(
        fig,
        0,
        largo_unidad,
        0,
        ancho_unidad,
        0,
        0.08,
        "#6b7280",
        0.35,
        "Piso unidad"
    )

    # Pared izquierda
    agregar_caja_3d(
        fig,
        0,
        largo_unidad,
        0,
        0.05,
        0,
        alto_unidad,
        "#93c5fd",
        0.16,
        "Pared izquierda"
    )

    # Pared derecha
    agregar_caja_3d(
        fig,
        0,
        largo_unidad,
        ancho_unidad - 0.05,
        ancho_unidad,
        0,
        alto_unidad,
        "#93c5fd",
        0.16,
        "Pared derecha"
    )

    # Cabina simbolica
    agregar_caja_3d(
        fig,
        -1.7,
        -0.1,
        0.25,
        ancho_unidad - 0.25,
        0,
        1.7,
        "#2563eb",
        0.55,
        "Cabina"
    )

    # Espacio ocupado por carga
    if volumen_total > 0:

        agregar_caja_3d(
            fig,
            0.25,
            largo_ocupado,
            0.18,
            ancho_unidad - 0.18,
            0.10,
            alto_unidad * min(max(porcentaje_ocupacion, 0.25), 0.95),
            "#f97316",
            0.18,
            "Volumen ocupado"
        )

    # Tarimas visuales
    tarima_largo = 1.15
    tarima_ancho = 1.00
    tarima_alto = 0.18
    caja_alto = 0.72

    max_tarimas_visuales = min(
        tarimas,
        24
    )

    posiciones_x = [
        0.40,
        1.80,
        3.20,
        4.60,
        6.00,
        7.40,
        8.80,
        10.20
    ]

    posiciones_y = [
        0.35,
        1.35
    ]

    contador = 0

    for x0 in posiciones_x:

        for y0 in posiciones_y:

            if contador >= max_tarimas_visuales:
                break

            contador += 1

            x1 = x0 + tarima_largo
            y1 = y0 + tarima_ancho

            agregar_caja_3d(
                fig,
                x0,
                x1,
                y0,
                y1,
                0.10,
                0.10 + tarima_alto,
                "#92400e",
                0.92,
                f"Tarima {contador}"
            )

            agregar_caja_3d(
                fig,
                x0 + 0.05,
                x1 - 0.05,
                y0 + 0.05,
                y1 - 0.05,
                0.10 + tarima_alto,
                0.10 + tarima_alto + caja_alto,
                "#fb923c",
                0.86,
                f"Carga {contador}"
            )

        if contador >= max_tarimas_visuales:
            break

    # Linea de capacidad ocupada
    fig.add_trace(

        go.Scatter3d(

            x=[
                0,
                largo_ocupado
            ],

            y=[
                ancho_unidad + 0.35,
                ancho_unidad + 0.35
            ],

            z=[
                0.08,
                0.08
            ],

            mode="lines+markers+text",

            line=dict(
                color="#16a34a",
                width=8
            ),

            marker=dict(
                size=5,
                color="#16a34a"
            ),

            text=[
                "",
                f"{porcentaje_volumen}% volumen"
            ],

            textposition="top center",

            name="% Volumen"
        )
    )

    fig.update_layout(

        title=(
            f"Simulación de carga - {vehiculo}"
        ),

        height=650,

        margin=dict(
            l=0,
            r=0,
            t=45,
            b=0
        ),

        scene=dict(

            xaxis_title="Largo unidad",

            yaxis_title="Ancho unidad",

            zaxis_title="Alto",

            bgcolor="white",

            aspectmode="manual",

            aspectratio=dict(
                x=4,
                y=1.2,
                z=1
            ),

            camera=dict(
                eye=dict(
                    x=1.8,
                    y=-2.1,
                    z=1.15
                )
            )
        ),

        showlegend=False
    )

    return fig, tarimas, porcentaje_peso, porcentaje_volumen


# =====================================================
# APP
# =====================================================

def alta_embarque_app():

    st.title(
        "🚛 Asignación de embarques a transporte"
    )

    st.caption(
        "Selección múltiple de hojas de carga y simulación visual del transporte."
    )

    st.divider()

    try:

        df_hojas = (
            obtener_hojas_carga_pendientes()
        )

        df_transportes = (
            obtener_transportes()
        )

    except Exception as e:

        st.error(
            "❌ Error cargando información."
        )

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

    st.session_state.df_hojas_sidebar = df_hojas

    df_hojas_filtrado = aplicar_filtros_sidebar(
        df_hojas
    )

    if df_hojas_filtrado.empty:

        st.warning(
            "No existen hojas de carga con los filtros seleccionados."
        )

        return

    # =====================================================
    # TABS
    # =====================================================

    (
        tab_seleccion,
        tab_resumen,
        tab_grafico
    ) = st.tabs(
        [
            "📦 Selección",
            "📋 Resumen",
            "📊 Simulación 3D"
        ]
    )

    # =====================================================
    # TAB SELECCION
    # =====================================================

    with tab_seleccion:

        st.subheader(
            "📦 Hojas de carga pendientes"
        )

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

            df_hojas_filtrado[columnas_mostrar],

            hide_index=True,

            use_container_width=True,

            height=420,

            column_config={

                "seleccionar": (
                    st.column_config.CheckboxColumn(
                        "Sel.",
                        default=False
                    )
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

        peso_seleccionado = round(

            df_seleccionadas["peso_total"].sum(),

            2

        ) if not df_seleccionadas.empty else 0

        volumen_seleccionado = round(

            df_seleccionadas["volumen_total"].sum(),

            2

        ) if not df_seleccionadas.empty else 0

        materiales_seleccionados = int(

            df_seleccionadas["materiales"].sum()

        ) if not df_seleccionadas.empty else 0

        st.divider()

        st.subheader(
            "🚛 Transportes sugeridos"
        )

        df_transportes_eval = (
            df_transportes.copy()
        )

        df_transportes_eval[
            "seleccionar"
        ] = False

        df_transportes_eval[
            "capacidad_peso"
        ] = pd.to_numeric(

            df_transportes_eval[
                "capacidad_peso"
            ],

            errors="coerce"

        ).fillna(0)

        df_transportes_eval[
            "capacidad_volumen"
        ] = pd.to_numeric(

            df_transportes_eval[
                "capacidad_volumen"
            ],

            errors="coerce"

        ).fillna(0)

        df_transportes_eval[
            "%_peso"
        ] = df_transportes_eval.apply(

            lambda row: round(

                (
                    peso_seleccionado
                    / row["capacidad_peso"]
                ) * 100,

                1

            ) if row[
                "capacidad_peso"
            ] > 0 else 0,

            axis=1
        )

        df_transportes_eval[
            "%_volumen"
        ] = df_transportes_eval.apply(

            lambda row: round(

                (
                    volumen_seleccionado
                    / row["capacidad_volumen"]
                ) * 100,

                1

            ) if row[
                "capacidad_volumen"
            ] > 0 else 0,

            axis=1
        )

        def validar_transporte(row):

            if df_seleccionadas.empty:

                return "⏳"

            if (
                peso_seleccionado
                > row["capacidad_peso"]
            ):

                return "❌"

            if (
                volumen_seleccionado
                > row["capacidad_volumen"]
            ):

                return "❌"

            if (
                row["%_peso"] >= 90
                or row["%_volumen"] >= 90
            ):

                return "⚠️"

            return "✅"

        df_transportes_eval[
            "validacion"
        ] = df_transportes_eval.apply(
            validar_transporte,
            axis=1
        )

        columnas_transporte = [

            "seleccionar",

            "codigo_transporte",

            "vehiculo",

            "placas",

            "operador",

            "codigo_ruta",

            "capacidad_peso",

            "capacidad_volumen",

            "%_peso",

            "%_volumen",

            "validacion"
        ]

        df_transportes_editor = st.data_editor(

            df_transportes_eval[
                columnas_transporte
            ],

            hide_index=True,

            use_container_width=True,

            height=300,

            column_config={

                "seleccionar": (
                    st.column_config.CheckboxColumn(
                        "Sel.",
                        default=False
                    )
                ),

                "codigo_transporte": "Transporte",

                "vehiculo": "Vehículo",

                "placas": "Placas",

                "operador": "Operador",

                "codigo_ruta": "Ruta",

                "capacidad_peso": "Cap. Peso",

                "capacidad_volumen": "Cap. Vol.",

                "%_peso": "% Peso",

                "%_volumen": "% Vol.",

                "validacion": "Estado"
            },

            disabled=[

                "codigo_transporte",

                "vehiculo",

                "placas",

                "operador",

                "codigo_ruta",

                "capacidad_peso",

                "capacidad_volumen",

                "%_peso",

                "%_volumen",

                "validacion"
            ],

            key="editor_transportes"
        )

        df_transportes_sel = (
            df_transportes_editor[
                df_transportes_editor[
                    "seleccionar"
                ] == True
            ]
        )

        transporte = None

        validacion_ok = False

        if len(df_transportes_sel) == 1:

            codigo = (
                df_transportes_sel.iloc[0][
                    "codigo_transporte"
                ]
            )

            transporte = (
                df_transportes_eval[
                    df_transportes_eval[
                        "codigo_transporte"
                    ].astype(str)
                    == str(codigo)
                ].iloc[0]
            )

            if df_seleccionadas.empty:

                st.info(
                    "Selecciona al menos una hoja de carga."
                )

            elif transporte["validacion"] == "❌":

                st.error(
                    "❌ Este transporte no tiene capacidad suficiente. Simula otro transporte antes de guardar."
                )

            else:

                validacion_ok = True

        elif len(df_transportes_sel) > 1:

            st.warning(
                "Selecciona solo un transporte."
            )

        else:

            st.info(
                "Selecciona un transporte para simular y confirmar."
            )

        st.divider()

        if st.button(

            "🚀 Confirmar asignación",

            use_container_width=True,

            disabled=not validacion_ok
        ):

            try:

                resultado = procesar_confirmacion_embarque(
                    df_seleccionadas,
                    transporte
                )

                st.success(
                    resultado["mensaje"]
                )

                st.write(
                    resultado["folios"]
                )

                st.download_button(
                    label="📥 Descargar Excel embarque",
                    data=resultado["excel"],
                    file_name="embarque.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            except Exception as e:

                st.error(
                    "❌ Error creando embarques."
                )

                st.exception(e)

    # =====================================================
    # TAB RESUMEN
    # =====================================================

    with tab_resumen:

        st.subheader(
            "📋 Resumen ejecutivo"
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "📦 Hojas",
            len(df_seleccionadas)
        )

        c2.metric(
            "📋 Materiales",
            materiales_seleccionados
        )

        c3.metric(
            "⚖️ Peso",
            peso_seleccionado
        )

        c4.metric(
            "📐 Volumen",
            volumen_seleccionado
        )

        st.divider()

        if not df_seleccionadas.empty:

            st.dataframe(
                df_seleccionadas,
                use_container_width=True,
                hide_index=True
            )

    # =====================================================
    # TAB GRAFICO
    # =====================================================

    with tab_grafico:

        st.subheader(
            "🚛 Simulación real de carga y cubicaje"
        )

        st.caption(
            "La simulación usa las hojas de carga seleccionadas y las capacidades reales del transporte seleccionado."
        )

        if df_seleccionadas.empty:

            st.warning(
                "Selecciona hojas de carga para iniciar la simulación."
            )

        elif transporte is None:

            st.warning(
                "Selecciona un transporte para validar peso, volumen y cubicaje."
            )

        else:

            capacidad_peso = float(
                transporte[
                    "capacidad_peso"
                ]
            )

            capacidad_volumen = float(
                transporte[
                    "capacidad_volumen"
                ]
            )

            vehiculo = str(
                transporte.get(
                    "vehiculo",
                    ""
                )
            )

            fig, tarimas_estimadas, porcentaje_peso, porcentaje_volumen = (
                crear_figura_simulacion_carga(
                    peso_seleccionado,
                    volumen_seleccionado,
                    capacidad_peso,
                    capacidad_volumen,
                    vehiculo
                )
            )

            estado_carga, color_estado = obtener_estado_carga(
                porcentaje_peso,
                porcentaje_volumen
            )

            panel1, panel2 = st.columns(
                [2.2, 1]
            )

            with panel1:

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            with panel2:

                st.markdown(
                    f"""
                    <div style="
                        background:white;
                        border-radius:18px;
                        padding:20px;
                        box-shadow:0 2px 12px rgba(0,0,0,.08);
                        border-left:6px solid {color_estado};
                        font-family:Arial;
                    ">
                        <div style="
                            font-size:22px;
                            font-weight:700;
                            margin-bottom:12px;
                        ">
                            {estado_carga}
                        </div>

                        <div style="line-height:2;font-size:15px;">
                            <b>Transporte:</b> {transporte['codigo_transporte']}<br>
                            <b>Vehículo:</b> {transporte['vehiculo']}<br>
                            <b>Placas:</b> {transporte['placas']}<br>
                            <b>Operador:</b> {transporte['operador']}<br>
                            <b>Ruta:</b> {transporte['codigo_ruta']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.write("")

                st.metric(
                    "📦 Tarimas estimadas",
                    tarimas_estimadas
                )

                st.metric(
                    "⚖️ Peso usado",
                    f"{peso_seleccionado} / {capacidad_peso}"
                )

                st.metric(
                    "📐 Volumen usado",
                    f"{volumen_seleccionado} / {capacidad_volumen}"
                )

            st.divider()

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "📦 Hojas seleccionadas",
                len(df_seleccionadas)
            )

            c2.metric(
                "📋 Materiales",
                materiales_seleccionados
            )

            c3.metric(
                "% Peso",
                f"{porcentaje_peso}%"
            )

            c4.metric(
                "% Volumen",
                f"{porcentaje_volumen}%"
            )

            st.progress(
                min(
                    int(porcentaje_peso),
                    100
                ),
                text=(
                    f"Ocupación peso: "
                    f"{porcentaje_peso}%"
                )
            )

            st.progress(
                min(
                    int(porcentaje_volumen),
                    100
                ),
                text=(
                    f"Ocupación volumen: "
                    f"{porcentaje_volumen}%"
                )
            )

            if (
                porcentaje_peso > 100
                or porcentaje_volumen > 100
            ):

                st.error(
                    "❌ No se puede guardar: la carga excede la capacidad del transporte. Selecciona otro transporte."
                )

            elif (
                porcentaje_peso >= 90
                or porcentaje_volumen >= 90
            ):

                st.warning(
                    "⚠️ Transporte cercano al límite. Se permite guardar, pero conviene revisar la operación."
                )

            else:

                st.success(
                    "✅ Transporte válido. La carga puede guardarse."
                )


if __name__ == "__main__":

    alta_embarque_app()
