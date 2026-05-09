import streamlit as st
import pandas as pd

from database import get_connection


#
def crear_tabla_auditoria():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS auditoria")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS auditoria (
            id_auditoria INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            modulo TEXT,
            accion TEXT,
            descripcion TEXT,
            fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()
    conn.close()
    
def registrar_auditoria(usuario, modulo, accion, descripcion):

    crear_tabla_auditoria()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO auditoria (
            usuario,
            modulo,
            accion,
            descripcion
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            usuario,
            modulo,
            accion,
            descripcion
        )
    )

    conn.commit()
    conn.close()


def consultar_auditoria_app():

    st.markdown("## 📜 Auditoría")
    st.caption("Historial de acciones realizadas en el sistema.")

    try:
        crear_tabla_auditoria()

        conn = get_connection()

        query = """
            SELECT *
            FROM auditoria
            ORDER BY id_auditoria DESC
        """

        df = pd.read_sql_query(query, conn)

        conn.close()

    except Exception as e:
        st.error("❌ No se pudo leer la auditoría desde la base de datos.")
        st.exception(e)
        return

    if df.empty:
        st.info("No hay registros de auditoría todavía.")
        return

    st.markdown("### 🔎 Filtros")

    col1, col2, col3 = st.columns(3)

    with col1:
        filtro_usuario = st.selectbox(
            "Usuario",
            ["Todos"] + sorted(df["usuario"].dropna().astype(str).unique().tolist())
        )

    with col2:
        filtro_modulo = st.selectbox(
            "Módulo",
            ["Todos"] + sorted(df["modulo"].dropna().astype(str).unique().tolist())
        )

    with col3:
        filtro_accion = st.selectbox(
            "Acción",
            ["Todos"] + sorted(df["accion"].dropna().astype(str).unique().tolist())
        )

    df_filtrado = df.copy()

    if filtro_usuario != "Todos":
        df_filtrado = df_filtrado[df_filtrado["usuario"].astype(str) == filtro_usuario]

    if filtro_modulo != "Todos":
        df_filtrado = df_filtrado[df_filtrado["modulo"].astype(str) == filtro_modulo]

    if filtro_accion != "Todos":
        df_filtrado = df_filtrado[df_filtrado["accion"].astype(str) == filtro_accion]

    st.divider()

    st.metric("Total eventos", len(df_filtrado))

    st.dataframe(
        df_filtrado,
        use_container_width=True
    )
