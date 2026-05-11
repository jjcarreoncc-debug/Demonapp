import streamlit as st
import pandas as pd

from materiales_db import consultar_materiales
from sigem_db import get_db_path


DB_NAME = "materiales"


def obtener_materiales():

    data = consultar_materiales()

    df = pd.DataFrame(data)

    return df


def consulta_material_app():

    st.title("🔍 Consulta de materiales")

    st.caption(
        "Maestros / Productos / Maestro de materiales / Consulta"
    )

    st.write(
        f"📂 Base usada: {get_db_path(DB_NAME)}"
    )

    # =====================================================
    # CARGAR DATOS
    # =====================================================

    try:

        df = obtener_materiales()

    except Exception as e:

        st.error("❌ Error consultando materiales")
        st.exception(e)
        return

    # =====================================================
    # VALIDAR
    # =====================================================

    if df.empty:
        st.warning("No hay materiales registrados")
        return

    st.success(f"✅ Registros encontrados: {len(df)}")

    # =====================================================
    # RENOMBRAR COLUMNAS
    # =====================================================

    columnas = {

        "codigo_material": "Código",
        "descripcion": "Descripción",
        "descripcion_larga": "Descripción larga",

        "categoria": "Categoría",
        "familia": "Familia",
        "marca": "Marca",

        "tipo_material": "Tipo material",
        "estatus": "Estatus",

        "unidad_base": "Unidad",

        "controla_lote": "Control lote",
        "controla_serie": "Control serie",

        "peso": "Peso",
        "volumen": "Volumen",

        "largo": "Largo",
        "ancho": "Ancho",
        "alto": "Alto",

        "tipo_almacenamiento": "Tipo almacenamiento",

        "almacen_default": "Almacén",
        "ubicacion_default": "Ubicación",

        "rotacion_abc": "ABC",

        "costo_estandar": "Costo estándar",
        "precio_compra": "Precio compra",
        "precio_venta": "Precio venta",

        "moneda": "Moneda",
        "impuesto": "Impuesto",

        "margen_objetivo": "Margen objetivo",

        "stock_minimo": "Stock mínimo",
        "stock_maximo": "Stock máximo",

        "punto_reorden": "Punto reorden",

        "lead_time": "Lead time",

        "permite_negativo": "Permite negativo",
        "requiere_inspeccion": "Requiere inspección",

        "codigo_barras": "Código barras",
        "sku_base": "SKU",

        "codigo_sap": "Código SAP",

        "proveedor_principal": "Proveedor",

        "usuario_creacion": "Usuario creación"

    }

    df = df.rename(columns=columnas)

    # =====================================================
    # FILTROS
    # =====================================================

    st.markdown("---")
    st.subheader("🎯 Filtros")

    c1, c2, c3 = st.columns(3)

    with c1:

        filtro_codigo = st.text_input(
            "Código"
        )

        categorias = (
            ["Todas"] +
            sorted(
                df["Categoría"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )
        )

        filtro_categoria = st.selectbox(
            "Categoría",
            categorias
        )

    with c2:

        filtro_descripcion = st.text_input(
            "Descripción"
        )

        filtro_familia = st.text_input(
            "Familia"
        )

    with c3:

        estatus = (
            ["Todos"] +
            sorted(
                df["Estatus"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )
        )

        filtro_estatus = st.selectbox(
            "Estatus",
            estatus
        )

        unidades = (
            ["Todas"] +
            sorted(
                df["Unidad"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )
        )

        filtro_unidad = st.selectbox(
            "Unidad",
            unidades
        )

    # =====================================================
    # FILTRAR
    # =====================================================

    df_filtrado = df.copy()

    if filtro_codigo:

        df_filtrado = df_filtrado[
            df_filtrado["Código"]
            .astype(str)
            .str.contains(
                filtro_codigo,
                case=False,
                na=False
            )
        ]

    if filtro_descripcion:

        df_filtrado = df_filtrado[
            df_filtrado["Descripción"]
            .astype(str)
            .str.contains(
                filtro_descripcion,
                case=False,
                na=False
            )
        ]

    if filtro_categoria != "Todas":

        df_filtrado = df_filtrado[
            df_filtrado["Categoría"] == filtro_categoria
        ]

    if filtro_familia:

        df_filtrado = df_filtrado[
            df_filtrado["Familia"]
            .astype(str)
            .str.contains(
                filtro_familia,
                case=False,
                na=False
            )
        ]

    if filtro_estatus != "Todos":

        df_filtrado = df_filtrado[
            df_filtrado["Estatus"] == filtro_estatus
        ]

    if filtro_unidad != "Todas":

        df_filtrado = df_filtrado[
            df_filtrado["Unidad"] == filtro_unidad
        ]

    # =====================================================
    # RESULTADOS
    # =====================================================

    st.markdown("---")
    st.subheader("📋 Resultados")

    if df_filtrado.empty:

        st.warning(
            "No se encontraron materiales"
        )

        return

    st.dataframe(

        df_filtrado,

        use_container_width=True,
        hide_index=True

    )

    # =====================================================
    # DETALLE
    # =====================================================

    st.markdown("---")
    st.subheader("📄 Detalle del material")

    material = st.selectbox(

        "Selecciona material",

        df_filtrado["Código"]
        .astype(str)
        .tolist()

    )

    fila = df_filtrado[
        df_filtrado["Código"]
        .astype(str) == material
    ].iloc[0]

    with st.expander(
        "📦 Información general",
        expanded=True
    ):

        c1, c2, c3 = st.columns(3)

        with c1:

            st.metric(
                "Código",
                fila.get("Código", "")
            )

            st.metric(
                "Categoría",
                fila.get("Categoría", "")
            )

            st.metric(
                "Familia",
                fila.get("Familia", "")
            )

        with c2:

            st.metric(
                "Unidad",
                fila.get("Unidad", "")
            )

            st.metric(
                "Marca",
                fila.get("Marca", "")
            )

            st.metric(
                "ABC",
                fila.get("ABC", "")
            )

        with c3:

            st.metric(
                "Tipo material",
                fila.get("Tipo material", "")
            )

            st.metric(
                "Estatus",
                fila.get("Estatus", "")
            )

            st.metric(
                "Lead time",
                fila.get("Lead time", 0)
            )

        st.info(
            f"Descripción: {fila.get('Descripción', '')}"
        )

    st.markdown("---")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.button("✏️ Modificar")

    with c2:
        st.button("❌ Baja")

    with c3:
        st.button("📥 Exportar")


if __name__ == "__main__":
    consulta_material_app()
