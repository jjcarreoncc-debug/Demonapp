
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
    "#be123c"
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


def agregar_texto_3d(fig, x, y, z, texto, color="#111827"):

    fig.add_trace(

        go.Scatter3d(

            x=[x],

            y=[y],

            z=[z],

            text=[texto],

            mode="text",

            textfont=dict(
                size=12,
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
            "#dc2626",
            "El vehículo excede su capacidad. Selecciona otra unidad."
        )

    if 94 <= maximo <= 100:
        return (
            "✅ ÓPTIMO",
            "#16a34a",
            "El vehículo está dentro del rango óptimo de ocupación."
        )

    if 80 <= maximo < 94:
        return (
            "⚠️ ACEPTABLE",
            "#f59e0b",
            "Aún hay espacio disponible. Puedes agregar más carga."
        )

    return (
        "ℹ️ BAJA OCUPACIÓN",
        "#2563eb",
        "El vehículo tiene mucho espacio disponible. Conviene consolidar más hojas."
    )


def estimar_tarimas_por_volumen(volumen_total):

    if volumen_total <= 0:
        return 0

    # Regla operativa de simulación:
    # 1 tarima promedio ocupa aprox. 3 m3
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
                "peso": peso,
                "volumen": volumen,
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

    largo_unidad = 13.6
    ancho_unidad = 2.44
    alto_unidad = 2.60

    tarima_largo = 1.15
    tarima_ancho = 1.00
    tarima_alto = 0.16
    carga_alto = 0.88

    carriles_y = [
        0.22,
        1.25
    ]

    posiciones_x = []
    x = 0.35

    while x + tarima_largo <= largo_unidad - 0.3:
        posiciones_x.append(
            round(
                x,
                2
            )
        )
        x += 1.28

    posiciones = []

    for px in posiciones_x:
        for py in carriles_y:
            posiciones.append(
                (
                    px,
                    py
                )
            )

    fig = go.Figure()

    # Caja transparente del transporte
    agregar_caja_3d(
        fig,
        0,
        largo_unidad,
        0,
        ancho_unidad,
        0,
        alto_unidad,
        "#bfdbfe",
        0.12,
        "Caja del vehículo"
    )

    # Piso
    agregar_caja_3d(
        fig,
        0,
        largo_unidad,
        0,
        ancho_unidad,
        0,
        0.08,
        "#111827",
        0.34,
        "Piso"
    )

    # Cabina simbólica
    agregar_caja_3d(
        fig,
        -1.55,
        -0.08,
        0.28,
        2.15,
        0,
        1.55,
        "#f8fafc",
        0.95,
        "Cabina"
    )

    agregar_caja_3d(
        fig,
        -1.45,
        -0.15,
        0.18,
        2.25,
        0,
        0.35,
        "#111827",
        0.80,
        "Chasis"
    )

    # Ruedas
    ruedas = [
        (-1.15, 0.12),
        (-1.15, 2.18),
        (3.2, 0.12),
        (3.2, 2.18),
        (8.8, 0.12),
        (8.8, 2.18),
        (10.0, 0.12),
        (10.0, 2.18)
    ]

    for i, (rx, ry) in enumerate(ruedas):

        agregar_caja_3d(
            fig,
            rx,
            rx + 0.35,
            ry,
            ry + 0.18,
            -0.35,
            0.05,
            "#020617",
            0.92,
            f"Rueda {i + 1}"
        )

    # Carga por hoja, cada hoja con color propio
    posicion_actual = 0

    for hoja in hojas:

        for t in range(
            hoja["tarimas"]
        ):

            if posicion_actual >= len(posiciones):
                break

            x0, y0 = posiciones[
                posicion_actual
            ]

            x1 = x0 + tarima_largo
            y1 = y0 + tarima_ancho

            z0 = 0.08
            z1 = z0 + tarima_alto

            texto_tarima = (
                f"Hoja: {hoja['folio']}<br>"
                f"Cliente: {hoja['cliente']}<br>"
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
                z0,
                z1,
                "#92400e",
                0.95,
                f"Tarima {hoja['numero']}",
                texto_tarima
            )

            agregar_caja_3d(
                fig,
                x0 + 0.03,
                x1 - 0.03,
                y0 + 0.03,
                y1 - 0.03,
                z1,
                z1 + carga_alto,
                hoja["color"],
                0.82,
                f"Embarque {hoja['numero']}",
                texto_tarima
            )

            posicion_actual += 1

    # Espacio disponible como tarimas transparentes
    for pos_libre in range(
        posicion_actual,
        min(
            len(posiciones),
            capacidad_tarimas
        )
    ):

        x0, y0 = posiciones[
            pos_libre
        ]

        agregar_caja_3d(
            fig,
            x0,
            x0 + tarima_largo,
            y0,
            y0 + tarima_ancho,
            0.08,
            0.08 + tarima_alto + carga_alto,
            "#d1d5db",
            0.15,
            "Espacio disponible"
        )

    # Etiquetas de medida
    agregar_texto_3d(
        fig,
        largo_unidad / 2,
        -0.45,
        0.05,
        f"Largo interno: {largo_unidad} m",
        "#2563eb"
    )

    agregar_texto_3d(
        fig,
        largo_unidad + 0.45,
        ancho_unidad / 2,
        alto_unidad / 2,
        f"Alto interno: {alto_unidad} m",
        "#2563eb"
    )

    agregar_texto_3d(
        fig,
        -0.55,
        ancho_unidad / 2,
        0.05,
        f"Ancho: {ancho_unidad} m",
        "#2563eb"
    )

    fig.update_layout(

        title=(
            f"Simulación de carga - {vehiculo}"
        ),

        height=660,

        margin=dict(
            l=0,
            r=0,
            t=40,
            b=0
        ),

        scene=dict(

            xaxis_title="Largo",

            yaxis_title="Ancho",

            zaxis_title="Alto",

            bgcolor="white",

            aspectmode="manual",

            aspectratio=dict(
                x=4.5,
                y=1.25,
                z=1
            ),

            camera=dict(
                eye=dict(
                    x=1.65,
                    y=-1.85,
                    z=0.92
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


def barra_html(valor, color):

    valor_limitado = min(
        max(
            float(valor),
            0
        ),
        100
    )

    return textwrap.dedent(f"""
    <div style="background:#e5e7eb;border-radius:999px;height:12px;overflow:hidden;">
        <div style="width:{valor_limitado}%;background:{color};height:12px;border-radius:999px;"></div>
    </div>
    """).strip()


def crear_html_etiqueta_embarque(
    folio_embarque,
    cliente,
    destino,
    transporte,
    peso,
    volumen,
    hojas,
    tarimas
):

    return textwrap.dedent(f"""
    <div style="
        border:2px solid #111827;
        border-radius:12px;
        padding:14px;
        background:white;
        font-family:Arial;
        color:#111827;
    ">
        <div style="
            text-align:center;
            font-size:22px;
            font-weight:800;
            margin-bottom:8px;
        ">
            {folio_embarque}
        </div>

        <div style="
            height:44px;
            background:
                repeating-linear-gradient(
                    90deg,
                    #111827 0px,
                    #111827 3px,
                    transparent 3px,
                    transparent 7px
                );
            margin-bottom:10px;
        "></div>

        <div style="font-size:13px;line-height:1.8;">
            <b>Cliente:</b> {cliente}<br>
            <b>Destino:</b> {destino}<br>
            <b>Transporte:</b> {transporte.get("codigo_transporte", "")}<br>
            <b>Vehículo:</b> {transporte.get("vehiculo", "")}<br>
            <b>Placas:</b> {transporte.get("placas", "")}<br>
            <b>Hojas:</b> {hojas}<br>
            <b>Tarimas:</b> {tarimas}<br>
            <b>Peso:</b> {peso} kg<br>
            <b>Volumen:</b> {volumen} m³
        </div>

        <div style="
            margin-top:10px;
            display:flex;
            justify-content:space-between;
            align-items:center;
            border-top:1px solid #d1d5db;
            padding-top:8px;
            font-size:12px;
        ">
            <b>SIGEM</b>
            <span>Uso interno - No remover</span>
        </div>
    </div>
    """).strip()


def crear_card_embarque(hoja):

    return textwrap.dedent(f"""
    <div style="
        border:1px solid #dbeafe;
        border-left:7px solid {hoja['color']};
        border-radius:12px;
        padding:12px;
        background:white;
        margin-bottom:10px;
        box-shadow:0 1px 8px rgba(0,0,0,.04);
        font-family:Arial;
    ">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div style="font-weight:800;color:#111827;">
                {hoja['numero']}. {hoja['folio']}
            </div>
            <div style="
                background:{hoja['color']};
                color:white;
                border-radius:8px;
                padding:4px 8px;
                font-size:12px;
                font-weight:700;
            ">
                ASIGNADO
            </div>
        </div>

        <div style="font-size:13px;line-height:1.8;margin-top:8px;">
            <b>Cliente:</b> {hoja['cliente']}<br>
            <b>Destino:</b> {hoja['destino']}<br>
            <b>Peso:</b> {hoja['peso']} kg<br>
            <b>Volumen:</b> {hoja['volumen']} m³<br>
            <b>Tarimas:</b> {hoja['tarimas']}
        </div>
    </div>
    """).strip()


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
            "🚛 Simulación de carga - visualización 3D"
        )

        st.caption(
            "Cada hoja de carga se representa como un bloque de color dentro del vehículo. El objetivo operativo es acercarse al 97% - 98% sin exceder peso, volumen ni tarimas."
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

            folio_simulado = generar_folio_embarque()

            cliente_principal = (
                df_seleccionadas["cliente"].iloc[0]
                if not df_seleccionadas.empty
                else ""
            )

            destino_principal = (
                df_seleccionadas["destino"].iloc[0]
                if not df_seleccionadas.empty
                else ""
            )

            col_izq, col_centro, col_der = st.columns(
                [1.05, 2.65, 1.15]
            )

            with col_izq:

                st.markdown(
                    "#### 📦 Embarques agregados"
                )

                st.caption(
                    f"{len(hojas_simulacion)} hojas seleccionadas"
                )

                for hoja in hojas_simulacion:

                    st.markdown(
                        crear_card_embarque(
                            hoja
                        ),
                        unsafe_allow_html=True
                    )

                st.markdown(
                    textwrap.dedent(f"""
                    <div style="
                        background:white;
                        border-radius:14px;
                        padding:14px;
                        box-shadow:0 2px 10px rgba(0,0,0,.07);
                        font-family:Arial;
                        margin-top:10px;
                    ">
                        <div style="font-weight:800;margin-bottom:10px;">
                            Totales actuales
                        </div>
                        <div style="font-size:13px;line-height:1.9;">
                            <b>Peso total:</b> {peso_seleccionado} kg<br>
                            <b>Volumen total:</b> {volumen_seleccionado} m³<br>
                            <b>Tarimas totales:</b> {tarimas_totales}<br>
                            <b>Hojas incluidas:</b> {len(hojas_simulacion)}
                        </div>
                    </div>
                    """).strip(),
                    unsafe_allow_html=True
                )

            with col_centro:

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

                m1, m2, m3, m4, m5 = st.columns(5)

                m1.metric(
                    "📦 Tarimas",
                    f"{tarimas_totales}",
                    f"de {capacidad_tarimas}"
                )

                m2.metric(
                    "⚖️ Peso",
                    f"{peso_seleccionado}",
                    f"{porcentaje_peso}%"
                )

                m3.metric(
                    "📐 Volumen",
                    f"{volumen_seleccionado}",
                    f"{porcentaje_volumen}%"
                )

                m4.metric(
                    "🟠 Cubicaje",
                    f"{porcentaje_volumen}%"
                )

                m5.metric(
                    "🎯 Meta",
                    "97% - 98%"
                )

                st.markdown(
                    "#### 🧭 Detalle por hoja"
                )

                df_detalle_sim = pd.DataFrame(
                    hojas_simulacion
                )

                if not df_detalle_sim.empty:

                    df_detalle_sim = df_detalle_sim[
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
                        df_detalle_sim,
                        use_container_width=True,
                        hide_index=True,
                        height=220
                    )

            with col_der:

                st.markdown(
                    textwrap.dedent(f"""
                    <div style="
                        background:white;
                        border-radius:16px;
                        padding:16px;
                        box-shadow:0 2px 12px rgba(0,0,0,.08);
                        border-left:6px solid {color_estado};
                        font-family:Arial;
                    ">
                        <div style="
                            font-size:20px;
                            font-weight:800;
                            color:{color_estado};
                            margin-bottom:10px;
                        ">
                            {estado_ocupacion}
                        </div>

                        <div style="font-size:13px;line-height:1.8;">
                            {mensaje_estado}
                        </div>
                    </div>
                    """).strip(),
                    unsafe_allow_html=True
                )

                st.write("")

                st.markdown(
                    textwrap.dedent(f"""
                    <div style="
                        background:white;
                        border-radius:16px;
                        padding:16px;
                        box-shadow:0 2px 12px rgba(0,0,0,.08);
                        font-family:Arial;
                    ">
                        <div style="font-size:17px;font-weight:800;margin-bottom:12px;">
                            🚛 Información vehículo
                        </div>
                        <div style="font-size:13px;line-height:1.9;">
                            <b>Transporte:</b> {transporte['codigo_transporte']}<br>
                            <b>Vehículo:</b> {transporte['vehiculo']}<br>
                            <b>Placas:</b> {transporte['placas']}<br>
                            <b>Operador:</b> {transporte['operador']}<br>
                            <b>Ruta:</b> {transporte['codigo_ruta']}<br>
                            <b>Cliente:</b> {cliente_principal}<br>
                            <b>Destino:</b> {destino_principal}
                        </div>
                    </div>
                    """).strip(),
                    unsafe_allow_html=True
                )

                st.write("")

                color_peso = (
                    "#dc2626"
                    if porcentaje_peso > 100
                    else "#16a34a"
                )

                color_volumen = (
                    "#dc2626"
                    if porcentaje_volumen > 100
                    else "#f59e0b"
                )

                st.markdown(
                    textwrap.dedent(f"""
                    <div style="
                        background:white;
                        border-radius:16px;
                        padding:16px;
                        box-shadow:0 2px 12px rgba(0,0,0,.08);
                        font-family:Arial;
                    ">
                        <div style="font-size:17px;font-weight:800;margin-bottom:12px;">
                            📊 Capacidad del vehículo
                        </div>

                        <div style="font-size:13px;margin-bottom:6px;">
                            <b>Peso:</b> {peso_seleccionado} / {capacidad_peso} kg
                        </div>
                        {barra_html(porcentaje_peso, color_peso)}
                        <div style="font-size:12px;color:{color_peso};text-align:right;margin-top:3px;">
                            {porcentaje_peso}%
                        </div>

                        <div style="font-size:13px;margin-top:12px;margin-bottom:6px;">
                            <b>Volumen:</b> {volumen_seleccionado} / {capacidad_volumen} m³
                        </div>
                        {barra_html(porcentaje_volumen, color_volumen)}
                        <div style="font-size:12px;color:{color_volumen};text-align:right;margin-top:3px;">
                            {porcentaje_volumen}%
                        </div>

                        <div style="font-size:13px;margin-top:12px;margin-bottom:6px;">
                            <b>Tarimas:</b> {tarimas_totales} / {capacidad_tarimas}
                        </div>
                        {barra_html(porcentaje_tarimas, "#7c3aed")}
                        <div style="font-size:12px;color:#7c3aed;text-align:right;margin-top:3px;">
                            {porcentaje_tarimas}%
                        </div>
                    </div>
                    """).strip(),
                    unsafe_allow_html=True
                )

                st.write("")

                st.markdown(
                    crear_html_etiqueta_embarque(
                        folio_simulado,
                        cliente_principal,
                        destino_principal,
                        transporte,
                        peso_seleccionado,
                        volumen_seleccionado,
                        len(hojas_simulacion),
                        tarimas_totales
                    ),
                    unsafe_allow_html=True
                )

            st.divider()

            if (
                porcentaje_peso > 100
                or porcentaje_volumen > 100
                or porcentaje_tarimas > 100
            ):

                st.error(
                    "❌ No se puede guardar: la carga excede la capacidad del transporte. Selecciona otro transporte o reduce hojas de carga."
                )

            elif (
                94 <= max(
                    porcentaje_peso,
                    porcentaje_volumen,
                    porcentaje_tarimas
                ) <= 100
            ):

                st.success(
                    "✅ Ocupación óptima. La unidad está cerca de la meta de aprovechamiento."
                )

            else:

                st.info(
                    "ℹ️ Puedes agregar más hojas si deseas acercarte al objetivo de 97% - 98% de ocupación."
                )


if __name__ == "__main__":

    alta_embarque_app()
