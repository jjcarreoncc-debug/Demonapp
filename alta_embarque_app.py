
import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import math
import textwrap
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

COLORES_EMBARQUE = [
    "#2563eb",
    "#f97316",
    "#16a34a",
    "#9333ea",
    "#dc2626",
    "#0891b2",
    "#ca8a04",
    "#be123c",
    "#0f766e",
    "#7c2d12"
]


def agregar_caja_3d(
    fig,
    x0,
    x1,
    y0,
    y1,
    z0,
    z1,
    color,
    opacity,
    nombre,
    texto=None
):

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

            text=texto,

            hoverinfo="text" if texto else "name",

            showscale=False
        )
    )


def agregar_etiqueta_3d(
    fig,
    x,
    y,
    z,
    texto,
    color
):

    fig.add_trace(

        go.Scatter3d(

            x=[x],

            y=[y],

            z=[z],

            mode="text",

            text=[texto],

            textfont=dict(
                size=13,
                color=color
            ),

            showlegend=False,

            hoverinfo="none"
        )
    )


def obtener_estado_carga(
    porcentaje_peso,
    porcentaje_volumen,
    porcentaje_tarimas
):

    maximo = max(
        porcentaje_peso,
        porcentaje_volumen,
        porcentaje_tarimas
    )

    if maximo > 100:
        return (
            "❌ SOBRECÁPACIDAD",
            "red",
            "La carga excede la unidad. Prueba otro transporte."
        )

    if 97 <= maximo <= 100:
        return (
            "✅ ÓPTIMO 97%-100%",
            "green",
            "Ocupación ideal para reducir costo por espacio vacío."
        )

    if 90 <= maximo < 97:
        return (
            "🟢 MUY BUENO",
            "green",
            "La unidad está bien aprovechada, aún puede consolidarse más."
        )

    if 75 <= maximo < 90:
        return (
            "⚠️ ACEPTABLE",
            "orange",
            "Aún hay espacio importante disponible."
        )

    return (
        "ℹ️ BAJA OCUPACIÓN",
        "blue",
        "Conviene agregar más hojas o usar una unidad menor."
    )


def estimar_tarimas_por_volumen(volumen_total):

    if volumen_total <= 0:
        return 0

    # Estimación operativa para prueba:
    # 1 tarima promedio ocupa aprox. 3 m3.
    return max(
        1,
        math.ceil(volumen_total / 3)
    )


def preparar_hojas_simulacion(df_seleccionadas):

    hojas = []

    for idx, row in df_seleccionadas.reset_index(drop=True).iterrows():

        peso = float(
            pd.to_numeric(
                row.get(
                    "peso_total",
                    0
                ),
                errors="coerce"
            )
            or 0
        )

        volumen = float(
            pd.to_numeric(
                row.get(
                    "volumen_total",
                    0
                ),
                errors="coerce"
            )
            or 0
        )

        tarimas = estimar_tarimas_por_volumen(
            volumen
        )

        hojas.append(
            {
                "numero": idx + 1,
                "folio": row.get(
                    "folio_hoja_carga",
                    ""
                ),
                "pedido": row.get(
                    "pedido",
                    ""
                ),
                "cliente": row.get(
                    "cliente",
                    ""
                ),
                "destino": row.get(
                    "destino",
                    ""
                ),
                "peso": round(peso, 2),
                "volumen": round(volumen, 2),
                "materiales": int(
                    row.get(
                        "materiales",
                        0
                    )
                    or 0
                ),
                "tarimas": tarimas,
                "color": COLORES_EMBARQUE[
                    idx % len(COLORES_EMBARQUE)
                ]
            }
        )

    return hojas


def crear_figura_simulacion_carga(
    df_seleccionadas,
    transporte,
    peso_total,
    volumen_total
):

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

    hojas = preparar_hojas_simulacion(
        df_seleccionadas
    )

    tarimas_totales = sum(
        h["tarimas"]
        for h in hojas
    )

    capacidad_tarimas = max(
        math.ceil(
            capacidad_volumen / 3
        ),
        1
    )

    porcentaje_peso = round(
        (peso_total / capacidad_peso) * 100,
        1
    ) if capacidad_peso > 0 else 0

    porcentaje_volumen = round(
        (volumen_total / capacidad_volumen) * 100,
        1
    ) if capacidad_volumen > 0 else 0

    porcentaje_tarimas = round(
        (tarimas_totales / capacidad_tarimas) * 100,
        1
    ) if capacidad_tarimas > 0 else 0

    largo_unidad = 13.60
    ancho_unidad = 2.44
    alto_unidad = 2.70

    tarima_largo = 1.15
    tarima_ancho = 1.00
    tarima_alto = 0.16
    carga_alto = 0.82
    separacion_x = 1.28

    carriles_y = [
        0.22,
        1.25
    ]

    posiciones_x = []
    x = 0.35

    while x + tarima_largo <= largo_unidad - 0.30:
        posiciones_x.append(
            round(
                x,
                2
            )
        )
        x += separacion_x

    posiciones_piso = []

    for px in posiciones_x:
        for py in carriles_y:
            posiciones_piso.append(
                (
                    px,
                    py
                )
            )

    capacidad_piso = len(
        posiciones_piso
    )

    max_niveles = max(
        1,
        math.ceil(
            capacidad_tarimas / capacidad_piso
        )
    )

    alto_por_nivel = tarima_alto + carga_alto + 0.08

    fig = go.Figure()

    # Caja del vehículo transparente.
    agregar_caja_3d(
        fig,
        0,
        largo_unidad,
        0,
        ancho_unidad,
        0,
        alto_unidad,
        "#dbeafe",
        0.10,
        "Caja del vehículo"
    )

    # Piso de la unidad.
    agregar_caja_3d(
        fig,
        0,
        largo_unidad,
        0,
        ancho_unidad,
        0,
        0.08,
        "#111827",
        0.38,
        "Piso"
    )

    # Cabina y chasis.
    agregar_caja_3d(
        fig,
        -1.65,
        -0.10,
        0.28,
        2.16,
        0,
        1.55,
        "#f8fafc",
        0.95,
        "Cabina"
    )

    agregar_caja_3d(
        fig,
        -1.55,
        -0.15,
        0.18,
        2.28,
        0,
        0.35,
        "#111827",
        0.85,
        "Chasis"
    )

    ruedas = [
        (-1.20, 0.08),
        (-1.20, 2.18),
        (2.80, 0.08),
        (2.80, 2.18),
        (8.50, 0.08),
        (8.50, 2.18),
        (10.00, 0.08),
        (10.00, 2.18)
    ]

    for i, (rx, ry) in enumerate(ruedas):

        agregar_caja_3d(
            fig,
            rx,
            rx + 0.36,
            ry,
            ry + 0.20,
            -0.32,
            0.05,
            "#020617",
            0.94,
            f"Rueda {i + 1}"
        )

    posicion_actual = 0
    etiquetas = []

    for hoja in hojas:

        primera_posicion_hoja = None
        ultima_posicion_hoja = None

        for _ in range(
            hoja["tarimas"]
        ):

            nivel = posicion_actual // capacidad_piso
            pos_base = posicion_actual % capacidad_piso

            if nivel >= max_niveles:
                break

            x0, y0 = posiciones_piso[
                pos_base
            ]

            z_base = 0.08 + (
                nivel * alto_por_nivel
            )

            x1 = x0 + tarima_largo
            y1 = y0 + tarima_ancho

            z_tarima = z_base + tarima_alto
            z_carga = z_tarima + carga_alto

            texto_hover = (
                f"Hoja: {hoja['folio']}<br>"
                f"Cliente: {hoja['cliente']}<br>"
                f"Destino: {hoja['destino']}<br>"
                f"Peso hoja: {hoja['peso']} kg<br>"
                f"Volumen hoja: {hoja['volumen']} m3<br>"
                f"Tarimas hoja: {hoja['tarimas']}"
            )

            agregar_caja_3d(
                fig,
                x0,
                x1,
                y0,
                y1,
                z_base,
                z_tarima,
                "#92400e",
                0.96,
                f"Tarima {hoja['numero']}",
                texto_hover
            )

            agregar_caja_3d(
                fig,
                x0 + 0.04,
                x1 - 0.04,
                y0 + 0.04,
                y1 - 0.04,
                z_tarima,
                z_carga,
                hoja["color"],
                0.86,
                f"Embarque {hoja['numero']}",
                texto_hover
            )

            if primera_posicion_hoja is None:
                primera_posicion_hoja = (
                    x0,
                    y0,
                    z_carga
                )

            ultima_posicion_hoja = (
                x1,
                y1,
                z_carga
            )

            posicion_actual += 1

        if (
            primera_posicion_hoja is not None
            and ultima_posicion_hoja is not None
        ):

            x_etiqueta = (
                primera_posicion_hoja[0]
                + ultima_posicion_hoja[0]
            ) / 2

            y_etiqueta = (
                primera_posicion_hoja[1]
                + ultima_posicion_hoja[1]
            ) / 2

            z_etiqueta = min(
                max(
                    primera_posicion_hoja[2],
                    ultima_posicion_hoja[2]
                ) + 0.30,
                alto_unidad + 0.45
            )

            etiquetas.append(
                (
                    x_etiqueta,
                    y_etiqueta,
                    z_etiqueta,
                    f"E{hoja['numero']}<br>{hoja['folio']}",
                    hoja["color"]
                )
            )

    # Espacio libre visible como posiciones grises transparentes.
    limite_espacios = min(
        capacidad_tarimas,
        capacidad_piso * max_niveles
    )

    for pos_libre in range(
        posicion_actual,
        limite_espacios
    ):

        nivel = pos_libre // capacidad_piso
        pos_base = pos_libre % capacidad_piso

        x0, y0 = posiciones_piso[
            pos_base
        ]

        z_base = 0.08 + (
            nivel * alto_por_nivel
        )

        agregar_caja_3d(
            fig,
            x0,
            x0 + tarima_largo,
            y0,
            y0 + tarima_ancho,
            z_base,
            z_base + tarima_alto + carga_alto,
            "#d1d5db",
            0.12,
            "Espacio disponible"
        )

    # Etiquetas flotantes por embarque.
    for x_lab, y_lab, z_lab, texto_lab, color_lab in etiquetas:
        agregar_etiqueta_3d(
            fig,
            x_lab,
            y_lab,
            z_lab,
            texto_lab,
            color_lab
        )

    # Guías de dimensión.
    agregar_etiqueta_3d(
        fig,
        largo_unidad / 2,
        -0.45,
        0.10,
        f"Largo {largo_unidad} m",
        "#2563eb"
    )

    agregar_etiqueta_3d(
        fig,
        -0.55,
        ancho_unidad / 2,
        0.10,
        f"Ancho {ancho_unidad} m",
        "#2563eb"
    )

    agregar_etiqueta_3d(
        fig,
        largo_unidad + 0.40,
        ancho_unidad / 2,
        alto_unidad / 2,
        f"Alto {alto_unidad} m",
        "#2563eb"
    )

    fig.update_layout(

        title=(
            f"Simulación de apilamiento por embarque - {vehiculo}"
        ),

        height=720,

        margin=dict(
            l=0,
            r=0,
            t=45,
            b=0
        ),

        scene=dict(

            xaxis_title="Largo",

            yaxis_title="Ancho",

            zaxis_title="Alto",

            bgcolor="white",

            aspectmode="manual",

            aspectratio=dict(
                x=4.8,
                y=1.35,
                z=1.15
            ),

            camera=dict(
                eye=dict(
                    x=1.75,
                    y=-1.95,
                    z=1.05
                )
            )
        ),

        showlegend=False
    )

    return (
        fig,
        hojas,
        tarimas_totales,
        capacidad_tarimas,
        porcentaje_peso,
        porcentaje_volumen,
        porcentaje_tarimas
    )


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
            "🚛 Simulación de apilamiento y cubicaje"
        )

        st.caption(
            "Cada hoja de carga se identifica dentro de la gráfica como un bloque de color. El objetivo es acercarse al 97% - 98% de ocupación sin exceder peso, volumen ni posiciones de tarima."
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

            (
                fig,
                hojas_simulacion,
                tarimas_totales,
                capacidad_tarimas,
                porcentaje_peso,
                porcentaje_volumen,
                porcentaje_tarimas
            ) = crear_figura_simulacion_carga(
                df_seleccionadas,
                transporte,
                peso_seleccionado,
                volumen_seleccionado
            )

            (
                estado_ocupacion,
                color_estado,
                mensaje_estado
            ) = obtener_estado_carga(
                porcentaje_peso,
                porcentaje_volumen,
                porcentaje_tarimas
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            c1, c2, c3, c4, c5, c6 = st.columns(6)

            c1.metric(
                "Estado",
                estado_ocupacion
            )

            c2.metric(
                "Tarimas",
                f"{tarimas_totales}",
                f"de {capacidad_tarimas}"
            )

            c3.metric(
                "% Tarimas",
                f"{porcentaje_tarimas}%"
            )

            c4.metric(
                "% Peso",
                f"{porcentaje_peso}%"
            )

            c5.metric(
                "% Volumen",
                f"{porcentaje_volumen}%"
            )

            c6.metric(
                "Meta",
                "97% - 98%"
            )

            st.progress(
                min(
                    int(porcentaje_peso),
                    100
                ),
                text=f"Peso: {peso_seleccionado} / {capacidad_peso} kg - {porcentaje_peso}%"
            )

            st.progress(
                min(
                    int(porcentaje_volumen),
                    100
                ),
                text=f"Volumen: {volumen_seleccionado} / {capacidad_volumen} m³ - {porcentaje_volumen}%"
            )

            st.progress(
                min(
                    int(porcentaje_tarimas),
                    100
                ),
                text=f"Posiciones tarima: {tarimas_totales} / {capacidad_tarimas} - {porcentaje_tarimas}%"
            )

            if color_estado == "red":

                st.error(
                    mensaje_estado
                )

            elif color_estado == "orange":

                st.warning(
                    mensaje_estado
                )

            elif color_estado == "green":

                st.success(
                    mensaje_estado
                )

            else:

                st.info(
                    mensaje_estado
                )

            st.divider()

            st.subheader(
                "📋 Hojas incluidas en la simulación"
            )

            df_simulacion = pd.DataFrame(
                hojas_simulacion
            )

            if not df_simulacion.empty:

                df_simulacion = df_simulacion[
                    [
                        "numero",
                        "folio",
                        "cliente",
                        "destino",
                        "peso",
                        "volumen",
                        "tarimas"
                    ]
                ]

                st.dataframe(
                    df_simulacion,
                    use_container_width=True,
                    hide_index=True,
                    height=260
                )

            if (
                porcentaje_peso > 100
                or porcentaje_volumen > 100
                or porcentaje_tarimas > 100
            ):

                st.error(
                    "❌ No se puede guardar: la carga excede la capacidad del transporte. Selecciona otro transporte o reduce hojas de carga."
                )

            elif (
                97 <= max(
                    porcentaje_peso,
                    porcentaje_volumen,
                    porcentaje_tarimas
                ) <= 100
            ):

                st.success(
                    "✅ Ocupación óptima. La unidad está en el rango objetivo de aprovechamiento."
                )

            else:

                st.info(
                    "ℹ️ Puedes agregar más hojas si deseas acercarte al objetivo de 97% - 98% de ocupación."
                )


if __name__ == "__main__":

    alta_embarque_app()
