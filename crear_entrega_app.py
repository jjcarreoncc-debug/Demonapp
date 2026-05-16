import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

from sigem_db import get_db_path


# ============================================================
# CONEXIONES
# ============================================================
def get_connection_logistica():
    return sqlite3.connect(get_db_path("logistica"))


def get_connection_inventarios():
    return sqlite3.connect(get_db_path("inventarios"))


# ============================================================
# CREAR TABLAS DE ENTREGAS EN LOGÍSTICA
# ============================================================
def crear_tablas_entregas():
    conn = get_connection_logistica()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS entregas (
            id_entrega INTEGER PRIMARY KEY AUTOINCREMENT,
            folio_entrega TEXT UNIQUE NOT NULL,
            pedido TEXT,
            cliente TEXT,
            destino TEXT,
            fecha_entrega TEXT,
            fecha_programada TEXT,
            prioridad TEXT,
            estatus_entrega TEXT DEFAULT 'Pendiente',
            observaciones TEXT,
            usuario TEXT,
            fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS detalle_entrega (
            id_detalle_entrega INTEGER PRIMARY KEY AUTOINCREMENT,
            folio_entrega TEXT NOT NULL,
            pedido TEXT,
            codigo_material TEXT,
            descripcion TEXT,
            cantidad_pedida REAL,
            cantidad_reservada REAL,
            cantidad_surtida REAL DEFAULT 0,
            bodega TEXT,
            ubicacion TEXT,
            peso REAL DEFAULT 0,
            volumen REAL DEFAULT 0,
            tarimas REAL DEFAULT 0,
            estatus_detalle TEXT DEFAULT 'Pendiente',
            observaciones TEXT
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
# CREAR / ASEGURAR MOVIMIENTOS INVENTARIO
# ============================================================
def crear_tabla_movimientos_reserva():
    conn = get_connection_inventarios()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS movimientos_inventario (
            id_movimiento INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            tipo_movimiento TEXT,
            codigo_material TEXT,
            descripcion TEXT,
            cantidad REAL,
            costo_unitario REAL DEFAULT 0,
            total REAL DEFAULT 0,
            bodega TEXT,
            ubicacion TEXT,
            referencia TEXT,
            comentarios TEXT,
            usuario TEXT,
            folio_movimiento TEXT,
            tipo_documento TEXT,
            numero_documento TEXT,
            archivo_documento TEXT
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
# GENERAR FOLIO
# ============================================================
def generar_folio_entrega():
    conn = get_connection_logistica()
    cur = conn.cursor()

    fecha = datetime.now().strftime("%Y%m%d")

    cur.execute("""
        SELECT COUNT(*)
        FROM entregas
        WHERE folio_entrega LIKE ?
    """, (f"ENT-{fecha}-%",))

    consecutivo = cur.fetchone()[0] + 1
    conn.close()

    return f"ENT-{fecha}-{consecutivo:04d}"


# ============================================================
# OBTENER PEDIDOS PARA CREAR ENTREGA
# ============================================================
def obtener_pedidos_para_entrega():

    logistica_path = get_db_path("logistica")
    inventarios_path = get_db_path("inventarios")

    conn = sqlite3.connect(logistica_path)
    cur = conn.cursor()

    try:

        cur.execute(
            f"ATTACH DATABASE '{inventarios_path}' AS invdb"
        )

        query = """

            WITH stock_bodega AS (

                SELECT
                    codigo_material,
                    bodega,

                    SUM(
                        CASE
                            WHEN tipo_movimiento <> 'RESERVA'
                            THEN cantidad
                            ELSE 0
                        END
                    ) AS stock_actual,

                    SUM(
                        CASE
                            WHEN tipo_movimiento = 'RESERVA'
                            THEN cantidad
                            ELSE 0
                        END
                    ) AS stock_reservado

                FROM invdb.movimientos_inventario

                GROUP BY
                    codigo_material,
                    bodega
            ),

            stock_total AS (

                SELECT
                    codigo_material,

                    SUM(
                        CASE
                            WHEN tipo_movimiento <> 'RESERVA'
                            THEN cantidad
                            ELSE 0
                        END
                    ) AS stock_total,

                    SUM(
                        CASE
                            WHEN tipo_movimiento = 'RESERVA'
                            THEN cantidad
                            ELSE 0
                        END
                    ) AS reservado_total

                FROM invdb.movimientos_inventario

                GROUP BY
                    codigo_material
            )

            SELECT

                p.pedido,
                p.fecha,
                p.cliente,
                p.destino,
                p.estatus,

                d.codigo_material,
                d.descripcion,
                d.cantidad_pedida,
                d.bodega,
                d.ubicacion,

                COALESCE(sb.stock_actual, 0)
                AS stock_actual,

                COALESCE(sb.stock_reservado, 0)
                AS stock_reservado,

                (
                    COALESCE(sb.stock_actual, 0)
                    -
                    COALESCE(sb.stock_reservado, 0)
                ) AS stock_disponible,

                (
                    COALESCE(st.stock_total, 0)
                    -
                    COALESCE(st.reservado_total, 0)
                ) AS stock_total_disponible

            FROM pedidos p

            INNER JOIN detalle_pedido d
                ON p.pedido = d.pedido

            LEFT JOIN stock_bodega sb
                ON d.codigo_material = sb.codigo_material
                AND d.bodega = sb.bodega

            LEFT JOIN stock_total st
                ON d.codigo_material = st.codigo_material

            WHERE p.estatus IN (
                'Pendiente',
                'Parcial'
            )

            ORDER BY
                p.fecha,
                p.pedido,
                d.codigo_material

        """

        df = pd.read_sql_query(query, conn)

    except Exception as e:

        st.error(
            f"Error al consultar pedidos: {e}"
        )

        df = pd.DataFrame()

    conn.close()

    if df.empty:
        return df

    def calcular_semaforo(row):

        disponible_bodega = row["stock_disponible"]
        disponible_total = row["stock_total_disponible"]
        cantidad = row["cantidad_pedida"]

        if disponible_bodega >= cantidad:
            return "🟢 Listo"

        elif disponible_total >= cantidad:
            return "🟡 Requiere transferencia"

        else:
            return "🔴 Sin inventario"

    df["semaforo"] = df.apply(
        calcular_semaforo,
        axis=1
    )

    return df


# ============================================================
# GUARDAR ENTREGA DESDE PEDIDOS
# ============================================================
def guardar_entrega_desde_pedidos(folio, df_seleccionados, observaciones, usuario):
    logistica_path = get_db_path("logistica")
    inventarios_path = get_db_path("inventarios")

    conn = sqlite3.connect(logistica_path)
    cur = conn.cursor()

    try:
        cur.execute(f"ATTACH DATABASE '{inventarios_path}' AS invdb")

        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pedidos = df_seleccionados["pedido"].dropna().astype(str).unique()
        pedido_texto = ", ".join(pedidos)

        cliente = ", ".join(
            df_seleccionados["cliente"].dropna().astype(str).unique()
        )

        destino = ", ".join(
            df_seleccionados["destino"].dropna().astype(str).unique()
        )

        cur.execute("""
            INSERT INTO entregas (
                folio_entrega,
                pedido,
                cliente,
                destino,
                fecha_entrega,
                fecha_programada,
                prioridad,
                estatus_entrega,
                observaciones,
                usuario,
                fecha_creacion
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            folio,
            pedido_texto,
            cliente,
            destino,
            fecha_actual,
            "",
            "Normal",
            "Reservada",
            observaciones,
            usuario,
            fecha_actual
        ))

        for _, item in df_seleccionados.iterrows():

            cantidad = float(item["cantidad_pedida"])

            cur.execute("""
                INSERT INTO detalle_entrega (
                    folio_entrega,
                    pedido,
                    codigo_material,
                    descripcion,
                    cantidad_pedida,
                    cantidad_reservada,
                    cantidad_surtida,
                    bodega,
                    ubicacion,
                    peso,
                    volumen,
                    tarimas,
                    estatus_detalle,
                    observaciones
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                folio,
                item["pedido"],
                item["codigo_material"],
                item["descripcion"],
                cantidad,
                cantidad,
                0,
                item["bodega"],
                item["ubicacion"],
                0,
                0,
                0,
                "Reservado",
                observaciones
            ))

            cur.execute("""
                INSERT INTO invdb.movimientos_inventario (
                    fecha,
                    tipo_movimiento,
                    codigo_material,
                    descripcion,
                    cantidad,
                    costo_unitario,
                    total,
                    bodega,
                    ubicacion,
                    referencia,
                    comentarios,
                    usuario,
                    folio_movimiento,
                    tipo_documento,
                    numero_documento,
                    archivo_documento
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                fecha_actual,
                "RESERVA",
                item["codigo_material"],
                item["descripcion"],
                cantidad,
                0,
                0,
                item["bodega"],
                item["ubicacion"],
                folio,
                "Reserva generada por creación de entrega virtual",
                usuario,
                folio,
                "ENTREGA",
                item["pedido"],
                ""
            ))

        for pedido in pedidos:
            cur.execute("""
                UPDATE pedidos
                SET estatus = ?
                WHERE pedido = ?
            """, (
                "Asignado a entrega",
                pedido
            ))

        conn.commit()
        conn.close()

        return True, folio

    except Exception as e:
        conn.rollback()
        conn.close()
        return False, str(e)


# ============================================================
# ESTILOS VISUALES
# ============================================================
def aplicar_estilos():
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }

        .titulo-entrega {
            font-size: 34px;
            font-weight: 900;
            color: #1F4E79;
            margin-bottom: 0px;
        }

        .subtitulo-entrega {
            font-size: 16px;
            color: #666666;
            margin-bottom: 18px;
        }

        div[data-testid="stMetric"] {
            background: linear-gradient(135deg, #ffffff, #f4f8fb);
            padding: 16px;
            border-radius: 16px;
            border: 1px solid #dce6ef;
            box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
        }
        </style>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# PANTALLA PRINCIPAL
# ============================================================
def pantalla_crear_entrega():
    aplicar_estilos()
    crear_tablas_entregas()
    crear_tabla_movimientos_reserva()

    st.markdown(
        '<div class="titulo-entrega">🚚 Creación de Entregas Virtuales</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitulo-entrega">Selecciona pedidos con inventario disponible en la misma bodega para reservar producto y generar folio de entrega.</div>',
        unsafe_allow_html=True
    )

    df = obtener_pedidos_para_entrega()

    if df.empty:
        st.warning("No hay pedidos pendientes o parciales disponibles para crear entregas.")
        return

    total_lineas = len(df)
    total_pedidos = df["pedido"].nunique()
    listos = len(df[df["semaforo"] == "🟢 Listo"])
    transferencia = len(df[df["semaforo"] == "🟡 Requiere transferencia"])
    sin_inventario = len(df[df["semaforo"] == "🔴 Sin inventario"])

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Pedidos", total_pedidos)

    with col2:
        st.metric("Listos", listos)

    with col3:
        st.metric("Transferencia", transferencia)

    with col4:
        st.metric("Sin inventario", sin_inventario)

    with col5:
        st.metric("Total líneas", total_lineas)

    st.divider()

    col_filtros, col_contenido = st.columns([1.05, 5])

    with col_filtros:

        st.subheader("🔎 Filtros")

        filtro_cliente = st.selectbox(
            "Cliente",
            ["Todos"] + sorted(df["cliente"].dropna().astype(str).unique().tolist())
        )

        filtro_destino = st.selectbox(
            "Destino",
            ["Todos"] + sorted(df["destino"].dropna().astype(str).unique().tolist())
        )

        filtro_semaforo = st.selectbox(
            "Semáforo",
            [
                "Todos",
                "🟢 Listo",
                "🟡 Requiere transferencia",
                "🔴 Sin inventario"
            ]
        )

        buscar = st.text_input(
            "Buscar pedido/material"
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

    if filtro_semaforo != "Todos":
        df_filtrado = df_filtrado[
            df_filtrado["semaforo"] == filtro_semaforo
        ]

    if buscar.strip():
        texto = buscar.strip().lower()

        df_filtrado = df_filtrado[
            df_filtrado["pedido"].astype(str).str.lower().str.contains(texto, na=False)
            | df_filtrado["codigo_material"].astype(str).str.lower().str.contains(texto, na=False)
            | df_filtrado["descripcion"].astype(str).str.lower().str.contains(texto, na=False)
            | df_filtrado["cliente"].astype(str).str.lower().str.contains(texto, na=False)
        ]

    st.divider()

    st.subheader("📋 Pedidos disponibles para entrega virtual")

    df_editor = df_filtrado.copy()
    df_editor.insert(0, "seleccionar", False)

    df_editor["bloqueado"] = df_editor["semaforo"].apply(
        lambda x: "No" if x == "🟢 Listo" else "Sí"
    )

    columnas_mostrar = [
        "seleccionar",
        "semaforo",
        "pedido",
        "fecha",
        "cliente",
        "destino",
        "estatus",
        "codigo_material",
        "descripcion",
        "cantidad_pedida",
        "stock_actual",
        "stock_reservado",
        "stock_disponible",
        "stock_total_disponible",
        "bodega",
        "ubicacion",
        "bloqueado"
    ]

    df_editor = df_editor[columnas_mostrar]

    editado = st.data_editor(
        df_editor,
        use_container_width=True,
        hide_index=True,
        height=430,
        column_config={
            "seleccionar": st.column_config.CheckboxColumn("Seleccionar"),
            "semaforo": st.column_config.TextColumn("Semáforo"),
            "pedido": st.column_config.TextColumn("Pedido"),
            "fecha": st.column_config.TextColumn("Fecha"),
            "cliente": st.column_config.TextColumn("Cliente"),
            "destino": st.column_config.TextColumn("Destino"),
            "estatus": st.column_config.TextColumn("Estatus"),
            "codigo_material": st.column_config.TextColumn("Material"),
            "descripcion": st.column_config.TextColumn("Descripción"),
            "cantidad_pedida": st.column_config.NumberColumn("Cantidad"),
            "stock_actual": st.column_config.NumberColumn("Stock bodega"),
            "stock_reservado": st.column_config.NumberColumn("Reservado bodega"),
            "stock_disponible": st.column_config.NumberColumn("Disponible bodega"),
            "stock_total_disponible": st.column_config.NumberColumn("Disponible total"),
            "bodega": st.column_config.TextColumn("Bodega"),
            "ubicacion": st.column_config.TextColumn("Ubicación"),
            "bloqueado": st.column_config.TextColumn("Bloqueado")
        },
        disabled=[
            "semaforo",
            "pedido",
            "fecha",
            "cliente",
            "destino",
            "estatus",
            "codigo_material",
            "descripcion",
            "cantidad_pedida",
            "stock_actual",
            "stock_reservado",
            "stock_disponible",
            "stock_total_disponible",
            "bodega",
            "ubicacion",
            "bloqueado"
        ],
        key="tabla_creacion_entregas"
    )

    seleccionados = editado[editado["seleccionar"] == True].copy()

    seleccionados_validos = seleccionados[
        seleccionados["semaforo"] == "🟢 Listo"
    ].copy()

    seleccionados_invalidos = seleccionados[
        seleccionados["semaforo"] != "🟢 Listo"
    ].copy()

    st.divider()

    st.subheader("📦 Resumen de creación")

    colr1, colr2, colr3 = st.columns(3)

    with colr1:
        st.metric("Líneas seleccionadas", len(seleccionados))

    with colr2:
        st.metric("Válidas para entrega", len(seleccionados_validos))

    with colr3:
        st.metric("No válidas", len(seleccionados_invalidos))

    if not seleccionados_invalidos.empty:
        st.warning(
            "Hay líneas seleccionadas que requieren transferencia o no tienen inventario. No se tomarán para crear la entrega."
        )

    observaciones = st.text_area("Observaciones de la entrega virtual")

    folio = generar_folio_entrega()

    st.info(f"Folio a generar: {folio}")

    if st.button("🚚 Generar entrega virtual seleccionada", use_container_width=True):

        if seleccionados_validos.empty:
            st.error("Debes seleccionar al menos una línea con semáforo 🟢 Listo.")
            return

        usuario = st.session_state.get("usuario", "usuario_desarrollo")

        ok, resultado = guardar_entrega_desde_pedidos(
            folio=folio,
            df_seleccionados=seleccionados_validos,
            observaciones=observaciones,
            usuario=usuario
        )

        if ok:
            st.success(f"Entrega virtual creada correctamente con folio: {resultado}")
            st.balloons()
            st.rerun()
        else:
            st.error(f"Error al crear entrega virtual: {resultado}")


# ============================================================
# EJECUCIÓN DIRECTA
# ============================================================
if __name__ == "__main__":
    pantalla_crear_entrega()
