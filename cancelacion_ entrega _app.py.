
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

from sigem_db import get_db_path


# ============================================================#
# CONEXIONES
# ============================================================
def get_connection_logistica():
    return sqlite3.connect(get_db_path("logistica"))


def get_connection_inventarios():
    return sqlite3.connect(get_db_path("inventarios"))


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


# ============================================================
# TABLAS DE CANCELACION
# ============================================================
def crear_tablas_cancelacion():
    conn = get_connection_logistica()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS cancelaciones_entrega (
            id_cancelacion INTEGER PRIMARY KEY AUTOINCREMENT,
            folio_cancelacion TEXT UNIQUE NOT NULL,
            folio_entrega TEXT NOT NULL,
            pedido TEXT,
            cliente TEXT,
            destino TEXT,
            motivo TEXT,
            observaciones TEXT,
            usuario TEXT,
            fecha_cancelacion TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS detalle_cancelacion_entrega (
            id_detalle_cancelacion INTEGER PRIMARY KEY AUTOINCREMENT,
            folio_cancelacion TEXT NOT NULL,
            folio_entrega TEXT NOT NULL,
            pedido TEXT,
            codigo_material TEXT,
            descripcion TEXT,
            cantidad_liberada REAL,
            bodega TEXT,
            ubicacion TEXT,
            observaciones TEXT
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
# FOLIOS
# ============================================================
def generar_folio_cancelacion():
    conn = get_connection_logistica()
    cur = conn.cursor()

    fecha = datetime.now().strftime("%Y%m%d")

    cur.execute("""
        SELECT COUNT(*)
        FROM cancelaciones_entrega
        WHERE folio_cancelacion LIKE ?
    """, (f"CAN-{fecha}-%",))

    consecutivo = cur.fetchone()[0] + 1
    conn.close()

    return f"CAN-{fecha}-{consecutivo:04d}"


# ============================================================
# CONSULTA DE ENTREGAS
# ============================================================
def obtener_entregas_con_detalle():
    logistica_path = get_db_path("logistica")
    inventarios_path = get_db_path("inventarios")

    conn = sqlite3.connect(logistica_path)
    cur = conn.cursor()

    if not tabla_existe(conn, "entregas") or not tabla_existe(conn, "detalle_entrega"):
        conn.close()
        return pd.DataFrame()

    try:
        cur.execute(
            f"ATTACH DATABASE '{inventarios_path}' AS invdb"
        )

        query = """
            WITH inventario AS (
                SELECT
                    codigo_material,
                    bodega,
                    SUM(
                        CASE
                            WHEN UPPER(IFNULL(tipo_movimiento, '')) <> 'RESERVA'
                            THEN IFNULL(cantidad, 0)
                            ELSE 0
                        END
                    ) AS inventario_sistema,
                    SUM(
                        CASE
                            WHEN UPPER(IFNULL(tipo_movimiento, '')) = 'RESERVA'
                            THEN IFNULL(cantidad, 0)
                            ELSE 0
                        END
                    ) AS inventario_reservado
                FROM invdb.movimientos_inventario
                GROUP BY
                    codigo_material,
                    bodega
            )

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
                e.fecha_creacion,
                d.codigo_material,
                d.descripcion,
                d.cantidad_pedida,
                d.cantidad_reservada,
                d.cantidad_surtida,
                d.bodega,
                d.ubicacion,
                d.estatus_detalle,
                d.observaciones AS observaciones_detalle,
                COALESCE(i.inventario_sistema, 0) AS inventario_sistema,
                COALESCE(i.inventario_reservado, 0) AS inventario_reservado,
                (
                    COALESCE(i.inventario_sistema, 0)
                    -
                    COALESCE(i.inventario_reservado, 0)
                ) AS inventario_disponible
            FROM entregas e
            LEFT JOIN detalle_entrega d
                ON e.folio_entrega = d.folio_entrega
            LEFT JOIN inventario i
                ON d.codigo_material = i.codigo_material
                AND d.bodega = i.bodega
            ORDER BY
                e.fecha_creacion DESC,
                e.folio_entrega DESC,
                d.codigo_material
        """

        df = pd.read_sql_query(query, conn)

    except Exception as e:
        st.error(f"Error consultando entregas: {e}")
        df = pd.DataFrame()

    conn.close()

    if df.empty:
        return df

    for col in [
        "cantidad_pedida",
        "cantidad_reservada",
        "cantidad_surtida",
        "inventario_sistema",
        "inventario_reservado",
        "inventario_disponible"
    ]:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        ).fillna(0)

    df["semaforo"] = df["estatus_entrega"].apply(
        lambda x: "🔴 Cancelada" if str(x).strip().lower() == "cancelada" else "🟢 Activa"
    )

    return df


# ============================================================
# CANCELAR ENTREGA
# ============================================================
def cancelar_entrega(folio_entrega, motivo, observaciones, usuario):
    logistica_path = get_db_path("logistica")
    inventarios_path = get_db_path("inventarios")

    conn = sqlite3.connect(logistica_path)
    cur = conn.cursor()

    try:
        crear_tablas_cancelacion()

        cur.execute(
            f"ATTACH DATABASE '{inventarios_path}' AS invdb"
        )

        cur.execute("""
            SELECT
                folio_entrega,
                pedido,
                cliente,
                destino,
                estatus_entrega
            FROM entregas
            WHERE folio_entrega = ?
        """, (folio_entrega,))

        entrega = cur.fetchone()

        if entrega is None:
            conn.close()
            return False, "No se encontró la entrega seleccionada."

        if str(entrega[4]).strip().lower() == "cancelada":
            conn.close()
            return False, "La entrega ya está cancelada."

        cur.execute("""
            SELECT
                folio_entrega,
                pedido,
                codigo_material,
                descripcion,
                cantidad_reservada,
                bodega,
                ubicacion
            FROM detalle_entrega
            WHERE folio_entrega = ?
        """, (folio_entrega,))

        detalles = cur.fetchall()

        if not detalles:
            conn.close()
            return False, "La entrega no tiene detalle para cancelar."

        folio_cancelacion = generar_folio_cancelacion()
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cur.execute("""
            INSERT INTO cancelaciones_entrega (
                folio_cancelacion,
                folio_entrega,
                pedido,
                cliente,
                destino,
                motivo,
                observaciones,
                usuario,
                fecha_cancelacion
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            folio_cancelacion,
            entrega[0],
            entrega[1],
            entrega[2],
            entrega[3],
            motivo,
            observaciones,
            usuario,
            fecha_actual
        ))

        for item in detalles:
            cantidad_liberada = float(item[4] or 0)

            if cantidad_liberada <= 0:
                continue

            cur.execute("""
                INSERT INTO detalle_cancelacion_entrega (
                    folio_cancelacion,
                    folio_entrega,
                    pedido,
                    codigo_material,
                    descripcion,
                    cantidad_liberada,
                    bodega,
                    ubicacion,
                    observaciones
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                folio_cancelacion,
                item[0],
                item[1],
                item[2],
                item[3],
                cantidad_liberada,
                item[5],
                item[6],
                observaciones
            ))

            # La reserva se libera insertando RESERVA negativa.
            # Esto baja el inventario reservado y sube el disponible.
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
                item[2],
                item[3],
                cantidad_liberada * -1,
                0,
                0,
                item[5],
                item[6],
                folio_cancelacion,
                f"Liberación de reserva por cancelación de entrega {folio_entrega}",
                usuario,
                folio_cancelacion,
                "CANCELACION_ENTREGA",
                item[1],
                ""
            ))

        cur.execute("""
            UPDATE entregas
            SET estatus_entrega = ?,
                observaciones = COALESCE(observaciones, '') || ?
            WHERE folio_entrega = ?
        """, (
            "Cancelada",
            f"\nCancelada con folio {folio_cancelacion}. Motivo: {motivo}. {observaciones}",
            folio_entrega
        ))

        cur.execute("""
            UPDATE detalle_entrega
            SET estatus_detalle = ?
            WHERE folio_entrega = ?
        """, (
            "Cancelado",
            folio_entrega
        ))

        pedidos = [
            p.strip()
            for p in str(entrega[1]).split(",")
            if p.strip()
        ]

        for pedido in pedidos:
            cur.execute("""
                UPDATE pedidos
                SET estatus = ?
                WHERE pedido = ?
            """, (
                "Pendiente",
                pedido
            ))

        conn.commit()
        conn.close()

        return True, folio_cancelacion

    except Exception as e:
        conn.rollback()
        conn.close()
        return False, str(e)


# ============================================================
# ESTILOS
# ============================================================
def aplicar_estilos_cancelacion():
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }

        .titulo-cancelacion {
            font-size: 34px;
            font-weight: 900;
            color: #1F4E79;
            margin-bottom: 0px;
        }

        .subtitulo-cancelacion {
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
# COMPONENTES VISUALES
# ============================================================
def mostrar_kpis_entregas(df):
    entregas_total = df["folio_entrega"].nunique()
    pedidos_total = df["pedido"].nunique()
    lineas_total = len(df)

    activas = df[
        df["estatus_entrega"].astype(str).str.lower() != "cancelada"
    ]["folio_entrega"].nunique()

    canceladas = df[
        df["estatus_entrega"].astype(str).str.lower() == "cancelada"
    ]["folio_entrega"].nunique()

    reservado = df["cantidad_reservada"].sum()

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        st.metric("Entregas", entregas_total)

    with c2:
        st.metric("Activas", activas)

    with c3:
        st.metric("Canceladas", canceladas)

    with c4:
        st.metric("Pedidos", pedidos_total)

    with c5:
        st.metric("Líneas", lineas_total)

    with c6:
        st.metric("Reservado", f"{reservado:,.2f}")


def mostrar_grid_entregas(df):
    columnas = [
        "semaforo",
        "folio_entrega",
        "pedido",
        "cliente",
        "destino",
        "fecha_entrega",
        "estatus_entrega",
        "codigo_material",
        "descripcion",
        "cantidad_pedida",
        "cantidad_reservada",
        "cantidad_surtida",
        "inventario_disponible",
        "bodega",
        "ubicacion",
        "usuario"
    ]

    columnas = [
        col for col in columnas if col in df.columns
    ]

    st.dataframe(
        df[columnas],
        use_container_width=True,
        hide_index=True,
        height=430
    )

    csv = df[columnas].to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "📥 Descargar consulta CSV",
        data=csv,
        file_name=f"consulta_entregas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )


def mostrar_detalle_entrega(df):
    folios = sorted(
        df["folio_entrega"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    if not folios:
        st.warning("No existen entregas para consultar.")
        return

    folio_sel = st.selectbox(
        "Selecciona entrega",
        folios,
        key="detalle_folio_entrega"
    )

    df_det = df[
        df["folio_entrega"].astype(str) == folio_sel
    ].copy()

    if df_det.empty:
        st.warning("No se encontró detalle para la entrega seleccionada.")
        return

    encabezado = df_det.iloc[0]

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Folio", encabezado.get("folio_entrega", ""))

    with c2:
        st.metric("Pedido", encabezado.get("pedido", ""))

    with c3:
        st.metric("Cliente", encabezado.get("cliente", ""))

    with c4:
        st.metric("Estatus", encabezado.get("estatus_entrega", ""))

    st.info(
        f"Destino: {encabezado.get('destino', '')} | Observaciones: {encabezado.get('observaciones_entrega', '')}"
    )

    columnas = [
        "codigo_material",
        "descripcion",
        "cantidad_pedida",
        "cantidad_reservada",
        "cantidad_surtida",
        "inventario_disponible",
        "bodega",
        "ubicacion",
        "estatus_detalle"
    ]

    columnas = [
        col for col in columnas if col in df_det.columns
    ]

    st.dataframe(
        df_det[columnas],
        use_container_width=True,
        hide_index=True,
        height=330
    )


# ============================================================
# APP PRINCIPAL
# ============================================================
def cancelacion_app():
    aplicar_estilos_cancelacion()
    crear_tablas_cancelacion()

    st.markdown(
        '<div class="titulo-cancelacion">🚚 Consulta y Cancelación de Entregas</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitulo-cancelacion">Consulta folios de entrega, revisa detalle operativo y cancela entregas liberando inventario reservado.</div>',
        unsafe_allow_html=True
    )

    df = obtener_entregas_con_detalle()

    if df.empty:
        st.warning("No existen entregas para consultar o cancelar.")
        st.info("Primero genera una entrega virtual desde Creación de entregas.")
        return

    st.divider()

    col_filtros, col_contenido = st.columns([1.05, 5])

    with col_filtros:

        st.subheader("🔎 Filtros")

        folios = sorted(
            df["folio_entrega"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        clientes = sorted(
            df["cliente"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        pedidos = sorted(
            df["pedido"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        estatus = sorted(
            df["estatus_entrega"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        filtro_folio = st.selectbox(
            "Folio entrega",
            ["Todos"] + folios
        )

        filtro_cliente = st.selectbox(
            "Cliente",
            ["Todos"] + clientes
        )

        filtro_pedido = st.selectbox(
            "Pedido",
            ["Todos"] + pedidos
        )

        filtro_estatus = st.selectbox(
            "Estatus",
            ["Todos"] + estatus
        )

        buscar = st.text_input(
            "Buscar material / destino"
        )

    df_filtrado = df.copy()

    if filtro_folio != "Todos":
        df_filtrado = df_filtrado[
            df_filtrado["folio_entrega"].astype(str) == filtro_folio
        ]

    if filtro_cliente != "Todos":
        df_filtrado = df_filtrado[
            df_filtrado["cliente"].astype(str) == filtro_cliente
        ]

    if filtro_pedido != "Todos":
        df_filtrado = df_filtrado[
            df_filtrado["pedido"].astype(str) == filtro_pedido
        ]

    if filtro_estatus != "Todos":
        df_filtrado = df_filtrado[
            df_filtrado["estatus_entrega"].astype(str) == filtro_estatus
        ]

    if buscar.strip():
        texto = buscar.strip().lower()

        df_filtrado = df_filtrado[
            df_filtrado["codigo_material"].astype(str).str.lower().str.contains(texto, na=False)
            | df_filtrado["descripcion"].astype(str).str.lower().str.contains(texto, na=False)
            | df_filtrado["destino"].astype(str).str.lower().str.contains(texto, na=False)
            | df_filtrado["cliente"].astype(str).str.lower().str.contains(texto, na=False)
        ]

    with col_contenido:

        mostrar_kpis_entregas(df_filtrado)

        st.divider()

        tab_consulta, tab_detalle, tab_cancelacion = st.tabs(
            [
                "📋 Consulta entregas",
                "📦 Detalle entrega",
                "❌ Cancelación"
            ]
        )

        with tab_consulta:
            mostrar_grid_entregas(df_filtrado)

        with tab_detalle:
            mostrar_detalle_entrega(df_filtrado)

        with tab_cancelacion:

            st.subheader("❌ Cancelación de entrega")

            df_cancelables = df_filtrado[
                df_filtrado["estatus_entrega"].astype(str).str.lower() != "cancelada"
            ].copy()

            folios_cancelables = sorted(
                df_cancelables["folio_entrega"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            if not folios_cancelables:
                st.info("No hay entregas activas para cancelar en el filtro actual.")
                return

            folio_cancelar = st.selectbox(
                "Selecciona entrega a cancelar",
                folios_cancelables,
                key="folio_cancelar"
            )

            df_sel = df_cancelables[
                df_cancelables["folio_entrega"].astype(str) == folio_cancelar
            ].copy()

            encabezado = df_sel.iloc[0]

            c1, c2, c3, c4 = st.columns(4)

            with c1:
                st.metric("Entrega", encabezado.get("folio_entrega", ""))

            with c2:
                st.metric("Pedido", encabezado.get("pedido", ""))

            with c3:
                st.metric("Cliente", encabezado.get("cliente", ""))

            with c4:
                st.metric("Reservado", f"{df_sel['cantidad_reservada'].sum():,.2f}")

            st.warning(
                "Al cancelar, se genera folio de cancelación, se libera la reserva de inventario y el pedido regresa a Pendiente para poder generar otra entrega."
            )

            columnas_cancelacion = [
                "codigo_material",
                "descripcion",
                "cantidad_reservada",
                "inventario_disponible",
                "bodega",
                "ubicacion",
                "estatus_detalle"
            ]

            columnas_cancelacion = [
                col for col in columnas_cancelacion if col in df_sel.columns
            ]

            st.dataframe(
                df_sel[columnas_cancelacion],
                use_container_width=True,
                hide_index=True,
                height=260
            )

            motivo = st.selectbox(
                "Motivo de cancelación",
                [
                    "Cliente canceló",
                    "Error operativo",
                    "Reprogramación",
                    "Cambio logístico",
                    "Duplicidad",
                    "Falta inventario",
                    "Otro"
                ]
            )

            observaciones = st.text_area(
                "Observaciones de cancelación"
            )

            confirmar = st.checkbox(
                "Confirmo que deseo cancelar esta entrega y liberar el inventario reservado"
            )

            if st.button(
                "❌ Cancelar entrega seleccionada",
                use_container_width=True,
                disabled=not confirmar
            ):

                usuario = st.session_state.get(
                    "usuario",
                    "usuario_desarrollo"
                )

                ok, resultado = cancelar_entrega(
                    folio_entrega=folio_cancelar,
                    motivo=motivo,
                    observaciones=observaciones,
                    usuario=usuario
                )

                if ok:
                    st.success(
                        f"Entrega cancelada correctamente. Folio de cancelación: {resultado}"
                    )
                    st.balloons()
                    st.rerun()

                else:
                    st.error(
                        f"Error al cancelar entrega: {resultado}"
                    )


# ============================================================
# EJECUCION DIRECTA
# ============================================================
if __name__ == "__main__":
    cancelacion_app()
