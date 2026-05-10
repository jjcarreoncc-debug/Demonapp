import streamlit as st
import pandas as pd
import sqlite3


DB_NAME = "materiales.db"


def consulta_material_app():

    st.title("🔍 Consulta de materiales")

    try:

        conn = sqlite3.connect(DB_NAME)

        query = """
            SELECT *
            FROM materiales
            ORDER BY codigo_material
        """

        df = pd.read_sql_query(query, conn)

        conn.close()

    except Exception as e:

        st.error("❌ Error consultando materiales")
        st.exception(e)
        return

    if df.empty:
        st.warning("No hay materiales registrados")
        return

    st.success(f"✅ Registros encontrados: {len(df)}")

    df = df.rename(columns={
        "codigo_material": "Código",
        "descripcion": "Descripción",
        "categoria": "Categoría",
        "familia": "Familia",
        "unidad_base": "Unidad",
        "estatus": "Estatus",
        "stock_minimo": "Stock mínimo",
        "stock_maximo": "Stock máximo",
        "rotacion_abc": "ABC"
    })

    st.subheader("📋 Materiales")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    material = st.selectbox(
        "Selecciona material",
        df["Código"].astype(str).tolist()
    )

    fila = df[
        df["Código"].astype(str) == material
    ].iloc[0]

    st.subheader("📄 Detalle")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Código", fila.get("Código", ""))
        st.metric("Categoría", fila.get("Categoría", ""))

    with c2:
        st.metric("Unidad", fila.get("Unidad", ""))
        st.metric("Estatus", fila.get("Estatus", ""))

    with c3:
        st.metric("ABC", fila.get("ABC", ""))
        st.metric("Stock máximo", fila.get("Stock máximo", 0))

    st.info(f"Descripción: {fila.get('Descripción', '')}")


if __name__ == "__main__":
    consulta_material_app()
