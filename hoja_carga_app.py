
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import math
import plotly.graph_objects as go

from sigem_db import get_db_path


# ============================================================
# CONEXIONES
# ============================================================
def get_connection_logistica():
    conn = sqlite3.connect(get_db_path("logistica"))
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# UTILIDADES
# ============================================================
def tabla_existe(conn, tabla):
    try:
        df = pd.read_sql_query(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name = ?
            """,
            conn,
            params=(tabla,)
        )
        return not df.empty
    except Exception:
        return False


def columna_existe(conn, tabla, columna):
    try:
        df = pd.read_sql_query(
            f"PRAGMA table_info({tabla})",
            conn
        )

        if df.empty:
            return False

        return columna in df["name"].astype(str).tolist()

    except Exception:
        return False


def asegurar_columna(conn, tabla, columna, definicion):
    cur = conn.cursor()

    if not columna_existe(conn, tabla, columna):
        cur.execute(
            f"""
            ALTER TABLE {tabla}
            ADD COLUMN {columna} {definicion}
            """
        )
        conn.commit()


# ============================================================
# TABLAS HOJA DE CARGA
# ============================================================
def crear_tablas_hoja_carga():
    conn = get_connection_logistica()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS hojas_carga (
            id_hoja_carga INTEGER PRIMARY KEY AUTOINCREMENT,
            folio_hoja_carga TEXT UNIQUE NOT NULL,
            cliente TEXT,
            destino TEXT,
            pedido TEXT,
            folios_entrega TEXT,
            fecha_creacion TEXT,
            estatus_hoja TEXT DEFAULT 'Pendiente',
            total_entregas INTEGER DEFAULT 0,
            total_materiales INTEGER DEFAULT 0,
            total_piezas REAL DEFAULT 0,
            total_cajas REAL DEFAULT 0,
            total_tarimas REAL DEFAULT 0,
            peso_total REAL DEFAULT 0,
            volumen_total REAL DEFAULT 0,
            condiciones_cliente TEXT,
            observaciones TEXT,
            usuario TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS detalle_hoja_carga (
            id_detalle_hoja INTEGER PRIMARY KEY AUTOINCREMENT,
            folio_hoja_carga TEXT NOT NULL,
            folio_entrega TEXT,
            pedido TEXT,
            cliente TEXT,
            destino TEXT,
            codigo_material TEXT,
            descripcion TEXT,
            cantidad_reservada REAL DEFAULT 0,
            unidad_base TEXT,
            piezas_por_caja REAL DEFAULT 0,
            cajas_por_tarima REAL DEFAULT 0,
            cajas_calculadas REAL DEFAULT 0,
            tarimas_calculadas REAL DEFAULT 0,
            piezas_sobrantes REAL DEFAULT 0,
            peso_calculado REAL DEFAULT 0,
            volumen_calculado REAL DEFAULT 0,
            validacion TEXT,
            observaciones TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tarimas_hoja_carga (
            id_tarima INTEGER PRIMARY KEY AUTOINCREMENT,
            folio_hoja_carga TEXT NOT NULL,
            numero_tarima INTEGER,
            codigo_material TEXT,
            descripcion TEXT,
            cantidad_piezas REAL DEFAULT 0,
            cantidad_cajas REAL DEFAULT 0,
            peso_estimado REAL DEFAULT 0,
            volumen_estimado REAL DEFAULT 0,
            tipo_tarima TEXT,
            estatus_tarima TEXT DEFAULT 'Armada'
        )
        """
    )

    if tabla_existe(conn, "entregas"):
        asegurar_columna(conn, "entregas", "folio_hoja_carga", "TEXT")

    conn.commit()
    conn.close()


# ============================================================
# FOLIO HOJA DE CARGA
# ============================================================
def generar_folio_hoja_carga():
    conn = get_connection_logistica()
    cur = conn.cursor()

    fecha = datetime.now().strftime("%Y%m%d")

    cur.execute(
        """
        SELECT COUNT(*)
        FROM hojas_carga
        WHERE folio_hoja_carga LIKE ?
        """,
        (f"HC-{fecha}-%",)
    )

    consecutivo = cur.fetchone()[0] + 1
    conn.close()

    return f"HC-{fecha}-{consecutivo:04d}"


# ============================================================
# CONFIGURACION LOGISTICA BASE
# ============================================================
def obtener_config_material(row):
    """
    Modelo inicial.
    Si después existen columnas reales en maestro de materiales,
    aquí se conectan. Por ahora usa reglas estándar para poder probar.
    """

    codigo = str(row.get("codigo_material", "")).upper()
    descripcion = str(row.get("descripcion", "")).upper()

    piezas_por_caja = 20
    cajas_por_tarima = 12
    peso_por_pieza = 2.0
    volumen_por_pieza = 0.0075
    unidad_base = "PZA"

    if "CAJA" in descripcion:
        piezas_por_caja = 1
        cajas_por_tarima = 24
        peso_por_pieza = 8.0
        volumen_por_pieza = 0.04
        unidad_base = "CAJA"

    if "TAR" in codigo or "TARIMA" in descripcion:
        piezas_por_caja = 1
        cajas_por_tarima = 1
        peso_por_pieza = 120.0
        volumen_por_pieza = 1.2
        unidad_base = "TARIMA"

    return {
        "unidad_base": unidad_base,
        "piezas_por_caja": piezas_por_caja,
        "cajas_por_tarima": cajas_por_tarima,
        "peso_por_pieza": peso_por_pieza,
        "volumen_por_pieza": volumen_por_pieza
    }


def obtener_condiciones_cliente(cliente):
    """
    Modelo inicial por cliente.
    Más adelante se debe leer de maestro de clientes.
    """

    cliente_txt = str(cliente).strip().lower()

    condiciones = {
        "requiere_tarima": True,
        "tipo_tarima": "Tarima estándar 1.20 x 1.00 m",
        "altura_maxima_m": 1.60,
        "peso_maximo_kg": 500,
        "requiere_etiqueta": True,
        "requiere_emplayado": True,
        "observacion": "Validar armado, etiqueta y emplayado antes de liberar a logística."
    }

    if "walmart" in cliente_txt:
        condiciones["tipo_tarima"] = "Tarima estándar 1.20 x 1.00 m"
        condiciones["requiere_etiqueta"] = True
        condiciones["observacion"] = "Etiqueta visible por tarima y producto emplayado."

    elif "soriana" in cliente_txt:
        condiciones["tipo_tarima"] = "Tarima estándar"
        condiciones["requiere_etiqueta"] = True
        condiciones["observacion"] = "Separar por destino y validar documentos."

    elif "oxxo" in cliente_txt:
        condiciones["tipo_tarima"] = "Tarima estándar"
        condiciones["peso_maximo_kg"] = 450
        condiciones["observacion"] = "No exceder peso máximo por tarima."

    return condiciones


# ============================================================
# DATOS BASE
# ============================================================
def obtener_entregas_reservadas():
    conn = get_connection_logistica()

    if not tabla_existe(conn, "entregas") or not tabla_existe(conn, "detalle_entrega"):
        conn.close()
        return pd.DataFrame()

    try:
        df = pd.read_sql_query(
            """
            SELECT
                e.folio_entrega,
                e.pedido,
                e.cliente,
                e.destino,
                e.fecha_entrega,
                e.fecha_programada,
                e.prioridad,
                e.estatus_entrega,
                e.observaciones AS observaciones_entrega,
                e.usuario,

                d.codigo_material,
                d.descripcion,
                d.cantidad_pedida,
                d.cantidad_reservada,
                d.cantidad_surtida,
                d.bodega,
                d.ubicacion,
                d.peso,
                d.volumen,
                d.tarimas,
                d.estatus_detalle

            FROM entregas e

            INNER JOIN detalle_entrega d
                ON e.folio_entrega = d.folio_entrega

            WHERE IFNULL(e.estatus_entrega, '') IN (
                'Reservada',
                'Pendiente',
                'Lista para carga'
            )

            AND IFNULL(e.folio_hoja_carga, '') = ''

            ORDER BY
                e.fecha_creacion DESC,
                e.folio_entrega DESC,
                d.codigo_material
            """,
            conn
        )

    except Exception as e:
        st.error(f"Error consultando entregas reservadas: {e}")
        df = pd.DataFrame()

    conn.close()

    if df.empty:
        return df

    for col in [
        "cantidad_pedida",
        "cantidad_reservada",
        "cantidad_surtida",
        "peso",
        "volumen",
        "tarimas"
    ]:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        ).fillna(0)

    return df


def calcular_armado_hoja(df):
    registros = []
    tarimas = []
    numero_tarima = 1

    for _, row in df.iterrows():

        config = obtener_config_material(row)
        cantidad = float(row.get("cantidad_reservada", 0))

        piezas_por_caja = float(config["piezas_por_caja"])
        cajas_por_tarima = float(config["cajas_por_tarima"])

        if piezas_por_caja <= 0:
            piezas_por_caja = 1

        if cajas_por_tarima <= 0:
            cajas_por_tarima = 1

        cajas = math.ceil(cantidad / piezas_por_caja)
        tarimas_calculadas = math.ceil(cajas / cajas_por_tarima)

        capacidad_pzas_tarima = piezas_por_caja * cajas_por_tarima

        piezas_sobrantes = cantidad % capacidad_pzas_tarima

        peso = cantidad * float(config["peso_por_pieza"])
        volumen = cantidad * float(config["volumen_por_pieza"])

        validacion = "OK"

        if cantidad <= 0:
            validacion = "Sin cantidad reservada"

        if tarimas_calculadas <= 0:
            tarimas_calculadas = 1

        registros.append(
            {
                "folio_entrega": row.get("folio_entrega", ""),
                "pedido": row.get("pedido", ""),
                "cliente": row.get("cliente", ""),
                "destino": row.get("destino", ""),
                "codigo_material": row.get("codigo_material", ""),
                "descripcion": row.get("descripcion", ""),
                "cantidad_reservada": cantidad,
                "unidad_base": config["unidad_base"],
                "piezas_por_caja": piezas_por_caja,
                "cajas_por_tarima": cajas_por_tarima,
                "cajas_calculadas": cajas,
                "tarimas_calculadas": tarimas_calculadas,
                "piezas_sobrantes": piezas_sobrantes,
                "peso_calculado": peso,
                "volumen_calculado": volumen,
                "validacion": validacion,
                "observaciones": ""
            }
        )

        piezas_restantes = cantidad
        cajas_restantes = cajas

        for _ in range(int(tarimas_calculadas)):

            cajas_tarima = min(cajas_por_tarima, cajas_restantes)
            piezas_tarima = min(capacidad_pzas_tarima, piezas_restantes)

            peso_tarima = piezas_tarima * float(config["peso_por_pieza"])
            volumen_tarima = piezas_tarima * float(config["volumen_por_pieza"])

            tarimas.append(
                {
                    "numero_tarima": numero_tarima,
                    "codigo_material": row.get("codigo_material", ""),
                    "descripcion": row.get("descripcion", ""),
                    "cantidad_piezas": piezas_tarima,
                    "cantidad_cajas": cajas_tarima,
                    "peso_estimado": peso_tarima,
                    "volumen_estimado": volumen_tarima,
                    "tipo_tarima": "Tarima estándar"
                }
            )

            numero_tarima += 1
            piezas_restantes -= piezas_tarima
            cajas_restantes -= cajas_tarima

    return pd.DataFrame(registros), pd.DataFrame(tarimas)


# ============================================================
# GUARDAR HOJA DE CARGA
# ============================================================
def guardar_hoja_carga(folio, df_base, df_armado, df_tarimas, condiciones, observaciones, usuario):
    conn = get_connection_logistica()
    cur = conn.cursor()

    try:
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        clientes = df_base["cliente"].dropna().astype(str).unique().tolist()
        destinos = df_base["destino"].dropna().astype(str).unique().tolist()
        pedidos = df_base["pedido"].dropna().astype(str).unique().tolist()
        entregas = df_base["folio_entrega"].dropna().astype(str).unique().tolist()

        cliente = ", ".join(clientes)
        destino = ", ".join(destinos)
        pedido = ", ".join(pedidos)
        folios_entrega = ", ".join(entregas)

        condiciones_txt = (
            f"Tipo tarima: {condiciones.get('tipo_tarima', '')} | "
            f"Altura max: {condiciones.get('altura_maxima_m', '')} m | "
            f"Peso max: {condiciones.get('peso_maximo_kg', '')} kg | "
            f"Etiqueta: {condiciones.get('requiere_etiqueta', '')} | "
            f"Emplayado: {condiciones.get('requiere_emplayado', '')} | "
            f"Obs: {condiciones.get('observacion', '')}"
        )

        cur.execute(
            """
            INSERT INTO hojas_carga (
                folio_hoja_carga,
                cliente,
                destino,
                pedido,
                folios_entrega,
                fecha_creacion,
                estatus_hoja,
                total_entregas,
                total_materiales,
                total_piezas,
                total_cajas,
                total_tarimas,
                peso_total,
                volumen_total,
                condiciones_cliente,
                observaciones,
                usuario
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                folio,
                cliente,
                destino,
                pedido,
                folios_entrega,
                fecha_actual,
                "Pendiente logística",
                len(entregas),
                df_armado["codigo_material"].nunique(),
                float(df_armado["cantidad_reservada"].sum()),
                float(df_armado["cajas_calculadas"].sum()),
                float(df_tarimas["numero_tarima"].nunique()) if not df_tarimas.empty else 0,
                float(df_armado["peso_calculado"].sum()),
                float(df_armado["volumen_calculado"].sum()),
                condiciones_txt,
                observaciones,
                usuario
            )
        )

        for _, row in df_armado.iterrows():

            cur.execute(
                """
                INSERT INTO detalle_hoja_carga (
                    folio_hoja_carga,
                    folio_entrega,
                    pedido,
                    cliente,
                    destino,
                    codigo_material,
                    descripcion,
                    cantidad_reservada,
                    unidad_base,
                    piezas_por_caja,
                    cajas_por_tarima,
                    cajas_calculadas,
                    tarimas_calculadas,
                    piezas_sobrantes,
                    peso_calculado,
                    volumen_calculado,
                    validacion,
                    observaciones
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    folio,
                    row["folio_entrega"],
                    row["pedido"],
                    row["cliente"],
                    row["destino"],
                    row["codigo_material"],
                    row["descripcion"],
                    row["cantidad_reservada"],
                    row["unidad_base"],
                    row["piezas_por_caja"],
                    row["cajas_por_tarima"],
                    row["cajas_calculadas"],
                    row["tarimas_calculadas"],
                    row["piezas_sobrantes"],
                    row["peso_calculado"],
                    row["volumen_calculado"],
                    row["validacion"],
                    row["observaciones"]
                )
            )

        for _, row in df_tarimas.iterrows():

            cur.execute(
                """
                INSERT INTO tarimas_hoja_carga (
                    folio_hoja_carga,
                    numero_tarima,
                    codigo_material,
                    descripcion,
                    cantidad_piezas,
                    cantidad_cajas,
                    peso_estimado,
                    volumen_estimado,
                    tipo_tarima,
                    estatus_tarima
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    folio,
                    int(row["numero_tarima"]),
                    row["codigo_material"],
                    row["descripcion"],
                    row["cantidad_piezas"],
                    row["cantidad_cajas"],
                    row["peso_estimado"],
                    row["volumen_estimado"],
                    row["tipo_tarima"],
                    "Armada"
                )
            )

        for entrega in entregas:
            cur.execute(
                """
                UPDATE entregas
                SET estatus_entrega = ?,
                    folio_hoja_carga = ?
                WHERE folio_entrega = ?
                """,
                (
                    "Hoja de carga",
                    folio,
                    entrega
                )
            )

        conn.commit()
        conn.close()

        return True, folio

    except Exception as e:
        conn.rollback()
        conn.close()
        return False, str(e)



# ============================================================
# GRAFICO 3D ARMADO HOJA DE CARGA
# ============================================================
def agregar_caja_3d(fig, x0, y0, z0, dx, dy, dz, texto, color):
    x1 = x0 + dx
    y1 = y0 + dy
    z1 = z0 + dz

    vertices_x = [x0, x1, x1, x0, x0, x1, x1, x0]
    vertices_y = [y0, y0, y1, y1, y0, y0, y1, y1]
    vertices_z = [z0, z0, z0, z0, z1, z1, z1, z1]

    caras_i = [0, 0, 0, 1, 2, 3, 4, 4, 5, 6, 7, 4]
    caras_j = [1, 2, 3, 5, 6, 7, 5, 6, 6, 7, 4, 7]
    caras_k = [2, 3, 0, 6, 7, 4, 6, 7, 1, 2, 0, 3]

    fig.add_trace(
        go.Mesh3d(
            x=vertices_x,
            y=vertices_y,
            z=vertices_z,
            i=caras_i,
            j=caras_j,
            k=caras_k,
            opacity=0.88,
            color=color,
            name=texto,
            hovertext=texto,
            hoverinfo="text",
            showscale=False
        )
    )


def mostrar_grafico_armado_3d(df_tarimas):
    if df_tarimas.empty:
        st.info("No hay tarimas para graficar.")
        return

    df_plot = df_tarimas.copy()

    max_tarimas = 12

    if len(df_plot) > max_tarimas:
        st.warning(
            f"Se muestran las primeras {max_tarimas} tarimas para mantener legible la simulación."
        )
        df_plot = df_plot.head(max_tarimas)

    fig = go.Figure()

    ancho_tarima = 2.4
    fondo_tarima = 1.2
    alto_base = 0.12

    caja_x = 0.55
    caja_y = 0.35
    caja_z = 0.25

    separacion_tarimas = 3.0

    colores = [
        "#1F77B4",
        "#FF7F0E",
        "#2CA02C",
        "#D62728",
        "#9467BD",
        "#8C564B",
        "#E377C2",
        "#7F7F7F",
        "#BCBD22",
        "#17BECF"
    ]

    for idx, row in df_plot.reset_index(drop=True).iterrows():

        offset_x = idx * separacion_tarimas
        numero_tarima = int(row.get("numero_tarima", idx + 1))
        codigo_material = str(row.get("codigo_material", ""))
        descripcion = str(row.get("descripcion", ""))[:25]
        cantidad_cajas = int(max(1, math.ceil(float(row.get("cantidad_cajas", 1)))))
        cantidad_piezas = float(row.get("cantidad_piezas", 0))
        peso_estimado = float(row.get("peso_estimado", 0))
        volumen_estimado = float(row.get("volumen_estimado", 0))

        texto_base = (
            f"Tarima {numero_tarima}<br>"
            f"Material: {codigo_material}<br>"
            f"{descripcion}<br>"
            f"Piezas: {cantidad_piezas:,.2f}<br>"
            f"Cajas: {cantidad_cajas}<br>"
            f"Peso: {peso_estimado:,.2f} kg<br>"
            f"Volumen: {volumen_estimado:,.2f} m³"
        )

        agregar_caja_3d(
            fig,
            offset_x,
            0,
            0,
            ancho_tarima,
            fondo_tarima,
            alto_base,
            texto_base,
            "#8B5A2B"
        )

        cajas_por_fila = 4
        filas_por_cama = 3
        cajas_por_cama = cajas_por_fila * filas_por_cama

        color = colores[idx % len(colores)]

        for caja in range(cantidad_cajas):

            cama = caja // cajas_por_cama
            posicion_cama = caja % cajas_por_cama
            fila = posicion_cama // cajas_por_fila
            columna = posicion_cama % cajas_por_fila

            x = offset_x + 0.08 + columna * caja_x
            y = 0.08 + fila * caja_y
            z = alto_base + cama * caja_z

            texto_caja = (
                f"Tarima {numero_tarima}<br>"
                f"Caja {caja + 1}<br>"
                f"Material: {codigo_material}<br>"
                f"{descripcion}"
            )

            agregar_caja_3d(
                fig,
                x,
                y,
                z,
                caja_x * 0.9,
                caja_y * 0.9,
                caja_z * 0.9,
                texto_caja,
                color
            )

        fig.add_trace(
            go.Scatter3d(
                x=[offset_x + ancho_tarima / 2],
                y=[fondo_tarima + 0.25],
                z=[1.0],
                mode="text",
                text=[f"TAR-{numero_tarima}"],
                textposition="middle center",
                showlegend=False
            )
        )

    fig.update_layout(
        height=560,
        margin=dict(l=0, r=0, t=30, b=0),
        scene=dict(
            xaxis_title="Tarimas / posición",
            yaxis_title="Profundidad",
            zaxis_title="Altura",
            aspectmode="data"
        ),
        title="Simulación gráfica de armado por hoja de carga",
        showlegend=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )



# ============================================================
# ESTILOS
# ============================================================
def aplicar_estilos_hoja_carga():
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }

        .titulo-hoja {
            font-size: 34px;
            font-weight: 900;
            color: #1F4E79;
            margin-bottom: 0px;
        }

        .subtitulo-hoja {
            font-size: 16px;
            color: #666666;
            margin-bottom: 18px;
        }

        div[data-testid="stMetric"] {
            background: linear-gradient(135deg, #ffffff, #f4f8fb);
            padding: 14px;
            border-radius: 14px;
            border: 1px solid #dce6ef;
            box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
        }
        </style>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# APP PRINCIPAL
# ============================================================
def hoja_carga_app():
    aplicar_estilos_hoja_carga()
    crear_tablas_hoja_carga()

    st.markdown(
        '<div class="titulo-hoja">📦 Hoja de carga</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitulo-hoja">Generación de hoja de carga desde entregas reservadas, validando armado logístico por cliente y material.</div>',
        unsafe_allow_html=True
    )

    df = obtener_entregas_reservadas()

    if df.empty:
        st.warning(
            "No hay entregas reservadas disponibles para generar hoja de carga."
        )
        return

    st.divider()

    col_filtros, col_contenido = st.columns([1.05, 5])

    with col_filtros:

        st.subheader("🔎 Filtros")

        clientes = ["Todos"] + sorted(
            df["cliente"].dropna().astype(str).unique().tolist()
        )

        filtro_cliente = st.selectbox(
            "Cliente",
            clientes
        )

        destinos = ["Todos"] + sorted(
            df["destino"].dropna().astype(str).unique().tolist()
        )

        filtro_destino = st.selectbox(
            "Destino",
            destinos
        )

        pedidos = ["Todos"] + sorted(
            df["pedido"].dropna().astype(str).unique().tolist()
        )

        filtro_pedido = st.selectbox(
            "Pedido",
            pedidos
        )

        buscar = st.text_input(
            "Buscar entrega/material"
        )

    df_filtrado = df.copy()

    if filtro_cliente != "Todos":
        df_filtrado = df_filtrado[
            df_filtrado["cliente"].astype(str) == filtro_cliente
        ]

    if filtro_destino != "Todos":
        df_filtrado = df_filtrado[
            df_filtrado["destino"].astype(str) == filtro_destino
        ]

    if filtro_pedido != "Todos":
        df_filtrado = df_filtrado[
            df_filtrado["pedido"].astype(str) == filtro_pedido
        ]

    if buscar.strip():
        texto = buscar.strip().lower()

        df_filtrado = df_filtrado[
            df_filtrado["folio_entrega"].astype(str).str.lower().str.contains(texto, na=False)
            | df_filtrado["pedido"].astype(str).str.lower().str.contains(texto, na=False)
            | df_filtrado["codigo_material"].astype(str).str.lower().str.contains(texto, na=False)
            | df_filtrado["descripcion"].astype(str).str.lower().str.contains(texto, na=False)
        ]

    with col_contenido:

        total_entregas = df_filtrado["folio_entrega"].nunique()
        total_pedidos = df_filtrado["pedido"].nunique()
        total_materiales = df_filtrado["codigo_material"].nunique()
        total_piezas = df_filtrado["cantidad_reservada"].sum()

        k1, k2, k3, k4 = st.columns(4)

        with k1:
            st.metric("Entregas", total_entregas)

        with k2:
            st.metric("Pedidos", total_pedidos)

        with k3:
            st.metric("Materiales", total_materiales)

        with k4:
            st.metric("Piezas reservadas", f"{total_piezas:,.2f}")

        st.divider()

        st.subheader("📋 Entregas disponibles para hoja de carga")

        resumen_entregas = (
            df_filtrado.groupby(
                [
                    "folio_entrega",
                    "pedido",
                    "cliente",
                    "destino",
                    "estatus_entrega"
                ]
            )
            .agg(
                materiales=("codigo_material", "nunique"),
                piezas=("cantidad_reservada", "sum")
            )
            .reset_index()
        )

        resumen_entregas.insert(0, "seleccionar", False)

        editado = st.data_editor(
            resumen_entregas,
            use_container_width=True,
            hide_index=True,
            height=280,
            column_config={
                "seleccionar": st.column_config.CheckboxColumn("Sel."),
                "folio_entrega": st.column_config.TextColumn("Entrega"),
                "pedido": st.column_config.TextColumn("Pedido"),
                "cliente": st.column_config.TextColumn("Cliente"),
                "destino": st.column_config.TextColumn("Destino"),
                "estatus_entrega": st.column_config.TextColumn("Estatus"),
                "materiales": st.column_config.NumberColumn("Mat."),
                "piezas": st.column_config.NumberColumn("Piezas")
            },
            disabled=[
                "folio_entrega",
                "pedido",
                "cliente",
                "destino",
                "estatus_entrega",
                "materiales",
                "piezas"
            ],
            key="tabla_entregas_hoja_carga"
        )

        entregas_seleccionadas = editado[
            editado["seleccionar"] == True
        ]["folio_entrega"].astype(str).tolist()

        if not entregas_seleccionadas:
            st.info(
                "Selecciona una o más entregas para simular y generar la hoja de carga."
            )
            return

        df_sel = df_filtrado[
            df_filtrado["folio_entrega"].astype(str).isin(entregas_seleccionadas)
        ].copy()

        clientes_sel = df_sel["cliente"].dropna().astype(str).unique().tolist()

        if len(clientes_sel) > 1:
            st.warning(
                "Seleccionaste entregas de más de un cliente. La hoja se puede generar, pero las condiciones logísticas pueden variar."
            )

        cliente_base = clientes_sel[0] if clientes_sel else ""

        condiciones = obtener_condiciones_cliente(cliente_base)

        df_armado, df_tarimas = calcular_armado_hoja(df_sel)

        st.divider()

        st.subheader("📦 Simulación de armado")

        r1, r2, r3, r4, r5 = st.columns(5)

        with r1:
            st.metric(
                "Tarimas",
                int(df_tarimas["numero_tarima"].nunique()) if not df_tarimas.empty else 0
            )

        with r2:
            st.metric(
                "Cajas",
                f"{df_armado['cajas_calculadas'].sum():,.0f}"
            )

        with r3:
            st.metric(
                "Piezas",
                f"{df_armado['cantidad_reservada'].sum():,.2f}"
            )

        with r4:
            st.metric(
                "Peso",
                f"{df_armado['peso_calculado'].sum():,.2f} kg"
            )

        with r5:
            st.metric(
                "Volumen",
                f"{df_armado['volumen_calculado'].sum():,.2f} m³"
            )

        tab_armado, tab_tarimas, tab_grafico, tab_validaciones = st.tabs(
            [
                "📄 Detalle armado",
                "📦 Tarimas",
                "🧊 Vista gráfica 3D",
                "✅ Validaciones"
            ]
        )

        with tab_armado:
            st.dataframe(
                df_armado,
                use_container_width=True,
                hide_index=True,
                height=300
            )

        with tab_tarimas:
            st.dataframe(
                df_tarimas,
                use_container_width=True,
                hide_index=True,
                height=300
            )

        with tab_grafico:
            mostrar_grafico_armado_3d(df_tarimas)

        with tab_validaciones:

            st.markdown("#### Condiciones logísticas del cliente")

            c1, c2, c3 = st.columns(3)

            with c1:
                st.metric(
                    "Requiere tarima",
                    "Sí" if condiciones.get("requiere_tarima") else "No"
                )

            with c2:
                st.metric(
                    "Altura máxima",
                    f"{condiciones.get('altura_maxima_m')} m"
                )

            with c3:
                st.metric(
                    "Peso máximo",
                    f"{condiciones.get('peso_maximo_kg')} kg"
                )

            st.info(
                condiciones.get("observacion", "")
            )

            alertas = []

            peso_max = float(condiciones.get("peso_maximo_kg", 0))

            if peso_max > 0 and not df_tarimas.empty:
                tarimas_pesadas = df_tarimas[
                    df_tarimas["peso_estimado"] > peso_max
                ]

                if not tarimas_pesadas.empty:
                    alertas.append(
                        "Existen tarimas que superan el peso máximo del cliente."
                    )

            if df_armado[
                df_armado["validacion"] != "OK"
            ].empty and not alertas:
                st.success(
                    "Validaciones correctas para generar hoja de carga."
                )
            else:
                for alerta in alertas:
                    st.warning(alerta)

        st.divider()

        st.subheader("📝 Generar hoja de carga")

        observaciones = st.text_area(
            "Observaciones de hoja de carga"
        )

        folio = generar_folio_hoja_carga()

        st.info(
            f"Folio a generar: {folio}"
        )

        if st.button(
            "📦 Generar hoja de carga",
            use_container_width=True
        ):

            usuario = st.session_state.get(
                "usuario",
                "usuario_desarrollo"
            )

            ok, resultado = guardar_hoja_carga(
                folio=folio,
                df_base=df_sel,
                df_armado=df_armado,
                df_tarimas=df_tarimas,
                condiciones=condiciones,
                observaciones=observaciones,
                usuario=usuario
            )

            if ok:
                st.success(
                    f"Hoja de carga generada correctamente: {resultado}"
                )
                st.balloons()
                st.rerun()
            else:
                st.error(
                    f"Error generando hoja de carga: {resultado}"
                )


# ============================================================
# EJECUCION DIRECTA
# ============================================================
if __name__ == "__main__":
    hoja_carga_app()
