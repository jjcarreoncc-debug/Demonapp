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
# CREAR TABLAS SI NO EXISTEN
# ============================================================
def crear_tablas_entregas():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS entregas (
            id_entrega INTEGER PRIMARY KEY AUTOINCREMENT,
            folio_entrega TEXT UNIQUE,
            fecha_entrega TEXT,
            solicitante TEXT,
            area TEXT,
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
            sku TEXT,
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
# OBTENER MATERIALES
# ============================================================
def obtener_materiales():
    conn = get_connection()

    query = """
        SELECT 
            sku,
            descripcion,
            unidad_medida,
            stock_actual,
            ubicacion
        FROM materiales
        WHERE activo = 1
        ORDER BY descripcion
    """

    try:
        df = pd.read_sql_query(query, conn)
    except Exception:
        df = pd.DataFrame(columns=[
            "sku", "descripcion", "unidad_medida", "stock_actual", "ubicacion"
        ])

    conn.close()
    return df


# ============================================================
# GUARDAR ENTREGA
# ============================================================
def guardar_entrega(
    folio,
    solicitante,
    area,
    destino,
    observaciones,
    detalle,
    usuario
):
    conn = get_connection()
    cur = conn.cursor()

    try:
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cur.execute("""
            INSERT INTO entregas (
                folio_entrega,
                fecha_entrega,
                solicitante,
                area,
                destino,
                observaciones,
                estatus,
                usuario_creacion,
                fecha_creacion
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            folio,
            fecha_actual,
            solicitante,
            area,
            destino,
            observaciones,
            "CREADA",
            usuario,
            fecha_actual
        ))

        id_entrega = cur.lastrowid

        for item in detalle:
            cur.execute("""
                INSERT INTO entregas_detalle (
                    id_entrega,
                    sku,
                    descripcion,
                    cantidad,
                    unidad_medida,
                    ubicacion
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                id_entrega,
                item["sku"],
                item["descripcion"],
                item["cantidad"],
                item["unidad_medida"],
                item["ubicacion"]
            ))

            cur.execute("""
                UPDATE materiales
                SET stock_actual = stock_actual - ?
                WHERE sku = ?
            """, (
                item["cantidad"],
                item["sku"]
            ))

        conn.commit()
        conn.close()
        return True, folio

    except Exception as e:
        conn.rollback()
        conn.close()
        return False, str(e)


# ============================================================
# PANTALLA PRINCIPAL
# ============================================================
def pantalla_crear_entrega():
    st.title("🚚 Creación de Entrega")

    crear_tablas_entregas()

    if "detalle_entrega" not in st.session_state:
        st.session_state.detalle_entrega = []

    folio = generar_folio_entrega()

    st.subheader("Encabezado de la entrega")

    col1, col2 = st.columns(2)

    with col1:
        st.text_input("Folio de entrega", value=folio, disabled=True)
        solicitante = st.text_input("Solicitante")
        area = st.text_input("Área solicitante")

    with col2:
        destino = st.text_input("Destino")
        observaciones = st.text_area("Observaciones")

    st.divider()

    st.subheader("Detalle de materiales")

    materiales = obtener_materiales()

    if materiales.empty:
        st.warning("No hay materiales activos registrados o no existe la tabla materiales.")
        return

    materiales["material_combo"] = (
        materiales["sku"].astype(str)
        + " - "
        + materiales["descripcion"].astype(str)
    )

    col1, col2, col3 = st.columns([4, 2, 2])

    with col1:
        material_sel = st.selectbox(
            "Material",
            materiales["material_combo"].tolist()
        )

    material_row = materiales[materiales["material_combo"] == material_sel].iloc[0]

    with col2:
        cantidad = st.number_input(
            "Cantidad",
            min_value=0.0,
            step=1.0
        )

    with col3:
        st.text_input(
            "Stock disponible",
            value=str(material_row["stock_actual"]),
            disabled=True
        )

    st.text_input(
        "Unidad de medida",
        value=str(material_row["unidad_medida"]),
        disabled=True
    )

    st.text_input(
        "Ubicación",
        value=str(material_row["ubicacion"]),
        disabled=True
    )

    if st.button("➕ Agregar material"):
        if cantidad <= 0:
            st.error("La cantidad debe ser mayor a cero.")
        elif cantidad > float(material_row["stock_actual"]):
            st.error("La cantidad solicitada excede el stock disponible.")
        else:
            st.session_state.detalle_entrega.append({
                "sku": material_row["sku"],
                "descripcion": material_row["descripcion"],
                "cantidad": cantidad,
                "unidad_medida": material_row["unidad_medida"],
                "ubicacion": material_row["ubicacion"]
            })
            st.success("Material agregado a la entrega.")

    st.divider()

    st.subheader("Materiales agregados")

    if st.session_state.detalle_entrega:
        df_detalle = pd.DataFrame(st.session_state.detalle_entrega)
        st.dataframe(df_detalle, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🧹 Limpiar detalle"):
                st.session_state.detalle_entrega = []
                st.rerun()

        with col2:
            if st.button("💾 Crear entrega"):
                if not solicitante.strip():
                    st.error("Debes capturar el solicitante.")
                    return

                if not area.strip():
                    st.error("Debes capturar el área solicitante.")
                    return

                if not destino.strip():
                    st.error("Debes capturar el destino.")
                    return

                usuario = st.session_state.get("usuario", "usuario_desarrollo")

                ok, resultado = guardar_entrega(
                    folio=folio,
                    solicitante=solicitante,
                    area=area,
                    destino=destino,
                    observaciones=observaciones,
                    detalle=st.session_state.detalle_entrega,
                    usuario=usuario
                )

                if ok:
                    st.success(f"Entrega creada correctamente: {resultado}")
                    st.session_state.detalle_entrega = []
                    st.balloons()
                else:
                    st.error(f"Error al crear entrega: {resultado}")

    else:
        st.info("Aún no hay materiales agregados.")


# ============================================================
# EJECUCIÓN DIRECTA
# ============================================================
if __name__ == "__main__":
    pantalla_crear_entrega()
