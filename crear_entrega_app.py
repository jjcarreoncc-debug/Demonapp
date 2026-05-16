import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime


DB_NAME = "sigem.db"


# ============================================================
# CONEXIÓN
# ============================================================
def get_connection():
    return sqlite3.connect(DB_NAME)


# ============================================================
# CREAR TABLAS DE ENTREGAS
# ============================================================
def crear_tablas_entregas():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS entregas (
            id_entrega INTEGER PRIMARY KEY AUTOINCREMENT,
            folio_entrega TEXT UNIQUE,
            fecha_entrega TEXT,
            cliente TEXT,
            destino TEXT,
            observaciones TEXT,
            estatus TEXT,
            usuario_creacion TEXT,
            fecha_creacion TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS entregas_detalle (
            id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
            id_entrega INTEGER,
            pedido TEXT,
            codigo_material TEXT,
            descripcion TEXT,
            cantidad REAL,
            unidad_medida TEXT,
            ubicacion TEXT,
            FOREIGN KEY(id_entrega) REFERENCES entregas(id_entrega)
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
# VALIDAR / AGREGAR COLUMNA STOCK_RESERVADO EN INVENTARIOS
# ============================================================
def asegurar_stock_reservado():
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("PRAGMA table_info(inventarios)")
        columnas = [row[1] for row in cur.fetchall()]

        if "stock_reservado" not in columnas:
            cur.execute("""
                ALTER TABLE inventarios
                ADD COLUMN stock_reservado REAL DEFAULT 0
            """)

        conn.commit()

    except Exception:
        pass

    conn.close()


# ============================================================
# GENERAR FOLIO
# ============================================================
def generar_folio_entrega():
    conn = get_connection()
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
    conn = get_connection()

    query = """
        SELECT
            p.pedido,
            p.fecha,
            p.cliente,
            p.destino,
            p.estatus_pedido,
            d.codigo_material,
            d.descripcion,
            d.cantidad,
            COALESCE(d.unidad_medida, '') AS unidad_medida,
            COALESCE(i.ubicacion, '') AS ubicacion,
            COALESCE(i.stock_actual, 0) AS stock_actual,
            COALESCE(i.stock_reservado, 0) AS stock_reservado,
            COALESCE(i.stock_actual, 0) - COALESCE(i.stock_reservado, 0) AS stock_disponible
        FROM pedidos p
        INNER JOIN pedidos_detalle d
            ON p.pedido = d.pedido
        LEFT JOIN inventarios i
            ON d.codigo_material = i.codigo_material
        WHERE p.estatus_pedido IN ('Pendiente', 'Parcial')
        ORDER BY p.fecha, p.pedido, d.codigo_material
    """

    try:
        df = pd.read_sql_query(query, conn)
    except Exception as e:
        st.error(f"Error al consultar pedidos: {e}")
        df = pd.DataFrame()

    conn.close()

    if df.empty:
        return df

    def calcular_semaforo(row):
        if row["stock_disponible"] >= row["cantidad"]:
            return "🟢 Listo"
        return "🔴 Sin inventario"

    df["semaforo"] = df.apply(calcular_semaforo, axis=1)

    return df


# ============================================================
# GUARDAR ENTREGA DESDE PEDIDOS
# ============================================================
def guardar_entrega_desde_pedidos(folio, df_seleccionados, observaciones, usuario):
    conn = get_connection()
    cur = conn.cursor()

    try:
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cliente = ", ".join(df_seleccionados["cliente"].dropna().astype(str).unique())
        destino = ", ".join(df_seleccionados["destino"].dropna().astype(str).unique())

        cur.execute("""
            INSERT INTO entregas (
                folio_entrega,
                fecha_entrega,
                cliente,
                destino,
                observaciones,
                estatus,
                usuario_creacion,
                fecha_creacion
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            folio,
            fecha_actual,
            cliente,
            destino,
            observaciones,
            "RESERVADA",
            usuario,
            fecha_actual
        ))

        id_entrega = cur.lastrowid

        for _, item in df_seleccionados.iterrows():

            cur.execute("""
                INSERT INTO entregas_detalle (
                    id_entrega,
                    pedido,
                    codigo_material,
                    descripcion,
                    cantidad,
                    unidad_medida,
                    ubicacion
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                id_entrega,
                item["pedido"],
                item["codigo_material"],
                item["descripcion"],
                float(item["cantidad"]),
                item["unidad_medida"],
                item["ubicacion"]
            ))

            # RESERVA INVENTARIO
            # NO DESCUENTA STOCK FÍSICO
            cur.execute("""
                UPDATE inventarios
                SET stock_reservado = COALESCE(stock_reservado, 0) + ?
                WHERE codigo_material = ?
            """, (
                float(item["cantidad"]),
                item["codigo_material"]
            ))

        pedidos = df_seleccionados["pedido"].dropna().astype(str).unique()

        for pedido in pedidos:
            cur.execute("""
                UPDATE pedidos
                SET estatus_pedido = ?
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
            font-size: 32px;
            font-weight: 800;
            color: #1F4E79;
            margin-bottom: 0px;
        }

        .subtitulo-entrega {
            font-size: 15px;
            color: #666666;
            margin-bottom: 20px;
        }

        .card-resumen {
            background: linear-gradient(135deg, #ffffff, #f4f8fb);
            padding: 18px;
            border-radius: 16px;
            border: 1px solid #dce6ef;
            box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
        }

        .seccion {
            background-color: #ffffff;
            padding: 18px;
            border-radius: 16px;
            border: 1px solid #e5e7eb;
            margin-top: 15px;
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
    asegurar_stock_reservado()

    st.markdown(
        '<div class="titulo-entrega">🚚 Creación de Entregas</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitulo-entrega">Selecciona pedidos listos para reservar inventario y generar un folio de entrega.</div>',
        unsafe_allow_html=True
    )

    df = obtener_pedidos_para_entrega()

    if df.empty:
        st.warning("No hay pedidos pendientes o parciales disponibles para crear entregas.")
        return

    total_lineas = len(df)
    total_pedidos = df["pedido"].nunique()
    listos = len(df[df["semaforo"] == "🟢 Listo"])
    sin_inventario = len(df[df["semaforo"] == "🔴 Sin inventario"])

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Pedidos", total_pedidos)

    with col2:
        st.metric("Líneas listas", listos)

    with col3:
        st.metric("Sin inventario", sin_inventario)

    with col4:
        st.metric("Total líneas", total_lineas)

    st.divider()

    st.subheader("Filtros de búsqueda")

    colf1, colf2, colf3, colf4 = st.columns(4)

    with colf1:
        filtro_cliente = st.selectbox(
            "Cliente",
            ["Todos"] + sorted(df["cliente"].dropna().astype(str).unique().tolist())
        )

    with colf2:
        filtro_destino = st.selectbox(
            "Destino",
            ["Todos"] + sorted(df["destino"].dropna().astype(str).unique().tolist())
        )

    with colf3:
        filtro_semaforo = st.selectbox(
            "Semáforo",
            ["Todos", "🟢 Listo", "🔴 Sin inventario"]
        )

    with colf4:
        buscar = st.text_input("Buscar pedido/material")

    df_filtrado = df.copy()

    if filtro_cliente != "Todos":
        df_filtrado = df_filtrado[df_filtrado["cliente"].astype(str) == filtro_cliente]

    if filtro_destino != "Todos":
        df_filtrado = df_filtrado[df_filtrado["destino"].astype(str) == filtro_destino]

    if filtro_semaforo != "Todos":
        df_filtrado = df_filtrado[df_filtrado["semaforo"] == filtro_semaforo]

    if buscar.strip():
        texto = buscar.strip().lower()
        df_filtrado = df_filtrado[
            df_filtrado["pedido"].astype(str).str.lower().str.contains(texto, na=False)
            | df_filtrado["codigo_material"].astype(str).str.lower().str.contains(texto, na=False)
            | df_filtrado["descripcion"].astype(str).str.lower().str.contains(texto, na=False)
            | df_filtrado["cliente"].astype(str).str.lower().str.contains(texto, na=False)
        ]

    st.divider()

    st.subheader("Pedidos disponibles para entrega")

    df_editor = df_filtrado.copy()
    df_editor.insert(0, "seleccionar", False)

    df_editor["bloqueado"] = df_editor["semaforo"].apply(
        lambda x: "Sí" if x != "🟢 Listo" else "No"
    )

    columnas_mostrar = [
        "seleccionar",
        "semaforo",
        "pedido",
        "fecha",
        "cliente",
        "destino",
        "estatus_pedido",
        "codigo_material",
        "descripcion",
        "cantidad",
        "stock_actual",
        "stock_reservado",
        "stock_disponible",
        "bloqueado"
    ]

    df_editor = df_editor[columnas_mostrar]

    editado = st.data_editor(
        df_editor,
        use_container_width=True,
        hide_index=True,
        height=420,
        column_config={
            "seleccionar": st.column_config.CheckboxColumn(
                "Seleccionar",
                help="Selecciona las líneas listas para crear entrega"
            ),
            "semaforo": st.column_config.TextColumn("Semáforo"),
            "pedido": st.column_config.TextColumn("Pedido"),
            "fecha": st.column_config.TextColumn("Fecha"),
            "cliente": st.column_config.TextColumn("Cliente"),
            "destino": st.column_config.TextColumn("Destino"),
            "estatus_pedido": st.column_config.TextColumn("Estatus"),
            "codigo_material": st.column_config.TextColumn("Material"),
            "descripcion": st.column_config.TextColumn("Descripción"),
            "cantidad": st.column_config.NumberColumn("Cantidad"),
            "stock_actual": st.column_config.NumberColumn("Stock físico"),
            "stock_reservado": st.column_config.NumberColumn("Reservado"),
            "stock_disponible": st.column_config.NumberColumn("Disponible"),
            "bloqueado": st.column_config.TextColumn("Bloqueado")
        },
        disabled=[
            "semaforo",
            "pedido",
            "fecha",
            "cliente",
            "destino",
            "estatus_pedido",
            "codigo_material",
            "descripcion",
            "cantidad",
            "stock_actual",
            "stock_reservado",
            "stock_disponible",
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

    st.subheader("Resumen de creación")

    colr1, colr2, colr3 = st.columns(3)

    with colr1:
        st.metric("Líneas seleccionadas", len(seleccionados))

    with colr2:
        st.metric("Válidas para entrega", len(seleccionados_validos))

    with colr3:
        st.metric("No válidas", len(seleccionados_invalidos))

    if not seleccionados_invalidos.empty:
        st.warning("Hay líneas seleccionadas sin inventario. No se tomarán para crear la entrega.")

    observaciones = st.text_area("Observaciones de la entrega")

    folio = generar_folio_entrega()

    st.info(f"Folio a generar: {folio}")

    if st.button("🚚 Generar entrega seleccionada", use_container_width=True):
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
            st.success(f"Entrega creada correctamente con folio: {resultado}")
            st.balloons()
            st.rerun()
        else:
            st.error(f"Error al crear entrega: {resultado}")


# ============================================================
# EJECUCIÓN DIRECTA
# ============================================================
if __name__ == "__main__":
    pantalla_crear_entrega()
