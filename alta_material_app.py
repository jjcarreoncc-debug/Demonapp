
import streamlit as st


def alta_material_app():

    st.title("➕ Alta de material")

    st.caption(
        "Maestros / Productos / Maestro de materiales / Alta de material"
    )

    with st.form("form_alta_material"):

        # =========================
        # DATOS GENERALES
        # =========================
        st.subheader("📋 Datos generales")

        c1, c2 = st.columns(2)

        with c1:
            codigo_material = st.text_input("Código material")
            descripcion = st.text_input("Descripción corta")
            descripcion_larga = st.text_area("Descripción larga")

            categoria = st.selectbox(
                "Categoría",
                [
                    "Materia prima",
                    "Producto terminado",
                    "Empaque",
                    "Refacción",
                    "Servicio"
                ]
            )

            familia = st.text_input("Familia")

        with c2:

            marca = st.text_input("Marca")

            tipo_material = st.selectbox(
                "Tipo material",
                [
                    "Almacenable",
                    "No almacenable",
                    "Servicio",
                    "Kit"
                ]
            )

            estatus = st.selectbox(
                "Estatus",
                [
                    "Activo",
                    "Bloqueado",
                    "Descontinuado"
                ]
            )

            unidad_base = st.selectbox(
                "Unidad base",
                [
                    "PZA",
                    "KG",
                    "LT",
                    "CJ",
                    "MT"
                ]
            )

            controla_lote = st.checkbox("Controla lote")
            controla_serie = st.checkbox("Controla serie")

        # =========================
        # DATOS LOGISTICOS
        # =========================
        st.markdown("---")
        st.subheader("📦 Datos logísticos")

        c1, c2, c3 = st.columns(3)

        with c1:
            peso = st.number_input(
                "Peso",
                min_value=0.0,
                step=0.01
            )

            volumen = st.number_input(
                "Volumen",
                min_value=0.0,
                step=0.01
            )

            largo = st.number_input(
                "Largo",
                min_value=0.0,
                step=0.01
            )

        with c2:

            ancho = st.number_input(
                "Ancho",
                min_value=0.0,
                step=0.01
            )

            alto = st.number_input(
                "Alto",
                min_value=0.0,
                step=0.01
            )

            tipo_almacenamiento = st.selectbox(
                "Tipo almacenamiento",
                [
                    "General",
                    "Refrigerado",
                    "Congelado",
                    "Peligroso",
                    "Alto valor"
                ]
            )

        with c3:

            almacen_default = st.text_input(
                "Almacén default"
            )

            ubicacion_default = st.text_input(
                "Ubicación default"
            )

            rotacion_abc = st.selectbox(
                "Clasificación ABC",
                [
                    "A",
                    "B",
                    "C"
                ]
            )

        # =========================
        # DATOS COMERCIALES
        # =========================
        st.markdown("---")
        st.subheader("💲 Datos comerciales")

        c1, c2, c3 = st.columns(3)

        with c1:

            costo_estandar = st.number_input(
                "Costo estándar",
                min_value=0.0,
                step=0.01
            )

            precio_compra = st.number_input(
                "Precio compra",
                min_value=0.0,
                step=0.01
            )

        with c2:

            precio_venta = st.number_input(
                "Precio venta",
                min_value=0.0,
                step=0.01
            )

            moneda = st.selectbox(
                "Moneda",
                [
                    "MXN",
                    "USD",
                    "EUR",
                    "COP"
                ]
            )

        with c3:

            impuesto = st.selectbox(
                "Impuesto",
                [
                    "IVA 0%",
                    "IVA 8%",
                    "IVA 16%",
                    "Exento"
                ]
            )

            margen_objetivo = st.number_input(
                "Margen objetivo %",
                min_value=0.0,
                step=0.5
            )

        # =========================
        # INVENTARIO
        # =========================
        st.markdown("---")
        st.subheader("📊 Inventario")

        c1, c2, c3 = st.columns(3)

        with c1:

            stock_minimo = st.number_input(
                "Stock mínimo",
                min_value=0.0,
                step=1.0
            )

            stock_maximo = st.number_input(
                "Stock máximo",
                min_value=0.0,
                step=1.0
            )

        with c2:

            punto_reorden = st.number_input(
                "Punto de reorden",
                min_value=0.0,
                step=1.0
            )

            lead_time = st.number_input(
                "Lead time días",
                min_value=0,
                step=1
            )

        with c3:

            permite_negativo = st.checkbox(
                "Permite inventario negativo"
            )

            requiere_inspeccion = st.checkbox(
                "Requiere inspección calidad"
            )

        # =========================
        # INTEGRACIONES
        # =========================
        st.markdown("---")
        st.subheader("🔗 Integraciones")

        c1, c2 = st.columns(2)

        with c1:

            codigo_barras = st.text_input(
                "Código de barras"
            )

            sku_base = st.text_input(
                "SKU base"
            )

        with c2:

            codigo_sap = st.text_input(
                "Código SAP / externo"
            )

            proveedor_principal = st.text_input(
                "Proveedor principal"
            )

        st.markdown("---")

        guardar = st.form_submit_button(
            "💾 Guardar material"
        )

        if guardar:

            st.success(
                "✅ Material listo para guardar."
            )

            st.write({
                "codigo_material": codigo_material,
                "descripcion": descripcion,
                "categoria": categoria,
                "unidad_base": unidad_base,
                "estatus": estatus
            })
