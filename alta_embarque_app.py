
import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
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

        validacion_ok = True

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

        else:

            validacion_ok = False

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
            "📊 Simulación visual de carga"
        )

        if df_seleccionadas.empty:

            st.warning(
                "Selecciona hojas."
            )

        elif transporte is None:

            st.warning(
                "Selecciona un transporte."
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

            porcentaje_peso = round(

                (
                    peso_seleccionado
                    / capacidad_peso
                ) * 100,

                1

            ) if capacidad_peso > 0 else 0

            porcentaje_volumen = round(

                (
                    volumen_seleccionado
                    / capacidad_volumen
                ) * 100,

                1

            ) if capacidad_volumen > 0 else 0

            largo = 10
            ancho = 4
            alto = 4

            volumen_ocupado = min(
                porcentaje_volumen / 100,
                1
            )

            largo_carga = (
                largo * volumen_ocupado
            )

            fig = go.Figure()

            fig.add_trace(

                go.Mesh3d(

                    x=[
                        0, largo,
                        largo, 0,
                        0, largo,
                        largo, 0
                    ],

                    y=[
                        0, 0,
                        ancho, ancho,
                        0, 0,
                        ancho, ancho
                    ],

                    z=[
                        0, 0,
                        0, 0,
                        alto, alto,
                        alto, alto
                    ],

                    opacity=0.10,

                    color="lightblue",

                    name="Transporte"
                )
            )

            fig.add_trace(

                go.Mesh3d(

                    x=[
                        0,
                        largo_carga,
                        largo_carga,
                        0,
                        0,
                        largo_carga,
                        largo_carga,
                        0
                    ],

                    y=[
                        0, 0,
                        ancho, ancho,
                        0, 0,
                        ancho, ancho
                    ],

                    z=[
                        0, 0,
                        0, 0,
                        alto, alto,
                        alto, alto
                    ],

                    opacity=0.75,

                    color="orange",

                    name="Carga"
                )
            )

            fig.update_layout(

                title=(
                    "Simulación 3D ocupación transporte"
                ),

                height=650,

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

                    aspectmode="data"
                )
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            st.divider()

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "% Peso",
                f"{porcentaje_peso}%"
            )

            c2.metric(
                "% Volumen",
                f"{porcentaje_volumen}%"
            )

            c3.metric(
                "Peso usado",
                peso_seleccionado
            )

            c4.metric(
                "Volumen usado",
                volumen_seleccionado
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


if __name__ == "__main__":

    alta_embarque_app()
