import streamlit as st


def set_opcion(menu, submenu, opcion):

    st.session_state.menu_inv = menu
    st.session_state.submenu_inv = submenu
    st.session_state.opcion_inv = opcion


def pantalla_placeholder(titulo):

    st.title("📦 Módulo de Inventarios")
    st.subheader(titulo)
    st.info("Pantalla en construcción.")


def sidebar_inventarios():

    with st.sidebar:

        st.markdown("## 🏢 SIGEM")
        st.markdown("### 📦 Inventarios")
        st.markdown("---")

        if "menu_inv" not in st.session_state:

            set_opcion(
                "Inicio",
                "Inicio",
                "🏠 Inicio"
            )

        # =================================================
        # DATOS MAESTROS
        # =================================================

        with st.expander(
            "📘 Datos Maestros",
            expanded=True
        ):

            # =================================================
            # PRODUCTOS
            # =================================================

            with st.expander(
                "📦 Productos",
                expanded=True
            ):

                with st.expander(
                    "📋 Maestro de materiales",
                    expanded=True
                ):

                    if st.button(
                        "➕ Alta de material"
                    ):

                        set_opcion(
                            "Datos Maestros",
                            "Productos",
                            "Alta de material"
                        )

                    if st.button(
                        "❌ Baja de material"
                    ):

                        set_opcion(
                            "Datos Maestros",
                            "Productos",
                            "Baja de material"
                        )

                    if st.button(
                        "🔍 Consulta de material"
                    ):

                        set_opcion(
                            "Datos Maestros",
                            "Productos",
                            "Consulta de material"
                        )

                with st.expander("🏷️ Clasificaciones"):

                    if st.button("Categorías"):

                        set_opcion(
                            "Datos Maestros",
                            "Productos",
                            "Categorías"
                        )

                    if st.button("Familias"):

                        set_opcion(
                            "Datos Maestros",
                            "Productos",
                            "Familias"
                        )

                    if st.button("Marcas"):

                        set_opcion(
                            "Datos Maestros",
                            "Productos",
                            "Marcas"
                        )

                with st.expander("🔢 Códigos"):

                    if st.button(
                        "Códigos de barras"
                    ):

                        set_opcion(
                            "Datos Maestros",
                            "Productos",
                            "Códigos de barras"
                        )

                    if st.button(
                        "SKU alternos"
                    ):

                        set_opcion(
                            "Datos Maestros",
                            "Productos",
                            "SKU alternos"
                        )

            # =================================================
            # EMPAQUES
            # =================================================

            with st.expander("📦 Empaques"):

                with st.expander("📏 Unidades"):

                    if st.button("Alta unidad"):

                        set_opcion(
                            "Datos Maestros",
                            "Empaques",
                            "Alta unidad"
                        )

                    if st.button(
                        "Consulta unidades"
                    ):

                        set_opcion(
                            "Datos Maestros",
                            "Empaques",
                            "Consulta unidades"
                        )

                with st.expander(
                    "📦 Tipos de empaque"
                ):

                    if st.button("Alta empaque"):

                        set_opcion(
                            "Datos Maestros",
                            "Empaques",
                            "Alta empaque"
                        )

                    if st.button(
                        "Consulta empaques"
                    ):

                        set_opcion(
                            "Datos Maestros",
                            "Empaques",
                            "Consulta empaques"
                        )

            # =================================================
            # UBICACIONES
            # =================================================

            with st.expander("📍 Ubicaciones"):

                with st.expander("🏬 Almacenes"):

                    if st.button("Alta almacén"):

                        set_opcion(
                            "Datos Maestros",
                            "Ubicaciones",
                            "Alta almacén"
                        )

                    if st.button(
                        "Consulta almacenes"
                    ):

                        set_opcion(
                            "Datos Maestros",
                            "Ubicaciones",
                            "Consulta almacenes"
                        )

                with st.expander("🧭 Zonas"):

                    if st.button("Alta zona"):

                        set_opcion(
                            "Datos Maestros",
                            "Ubicaciones",
                            "Alta zona"
                        )

                    if st.button(
                        "Consulta zonas"
                    ):

                        set_opcion(
                            "Datos Maestros",
                            "Ubicaciones",
                            "Consulta zonas"
                        )

                with st.expander(
                    "📌 Ubicaciones físicas"
                ):

                    if st.button("Alta ubicación"):

                        set_opcion(
                            "Datos Maestros",
                            "Ubicaciones",
                            "Alta ubicación"
                        )

                    if st.button(
                        "Consulta ubicaciones"
                    ):

                        set_opcion(
                            "Datos Maestros",
                            "Ubicaciones",
                            "Consulta ubicaciones"
                        )

        # =================================================
        # OPERACIÓN INVENTARIOS
        # =================================================

        with st.expander("⚙️ Operación Inventarios"):

            # =================================================
            # ENTRADAS
            # =================================================

            with st.expander("📥 Entradas"):

                with st.expander("Compra"):

                    if st.button(
                        "Registrar entrada compra"
                    ):

                        set_opcion(
                            "Operación Inventarios",
                            "Entradas",
                            "Registrar entrada compra"
                        )

                    if st.button(
                        "Consultar entradas compra"
                    ):

                        set_opcion(
                            "Operación Inventarios",
                            "Entradas",
                            "Consultar entradas compra"
                        )

                with st.expander("Ajuste"):

                    if st.button(
                        "Registrar entrada ajuste"
                    ):

                        set_opcion(
                            "Operación Inventarios",
                            "Entradas",
                            "Registrar entrada ajuste"
                        )

                    if st.button(
                        "Consultar entradas ajuste"
                    ):

                        set_opcion(
                            "Operación Inventarios",
                            "Entradas",
                            "Consultar entradas ajuste"
                        )

                if st.button(
                    "🚚 Embarque"
                ):

                    set_opcion(
                        "Operación Inventarios",
                        "Entradas",
                        "Embarque"
                    )

            # =================================================
            # SALIDAS
            # =================================================

            with st.expander("📤 Salidas"):

                with st.expander("Venta"):

                    if st.button(
                        "Registrar salida venta"
                    ):

                        set_opcion(
                            "Operación Inventarios",
                            "Salidas",
                            "Registrar salida venta"
                        )

                    if st.button(
                        "Consultar salidas venta"
                    ):

                        set_opcion(
                            "Operación Inventarios",
                            "Salidas",
                            "Consultar salidas venta"
                        )

                with st.expander("Merma"):

                    if st.button(
                        "Registrar merma"
                    ):

                        set_opcion(
                            "Operación Inventarios",
                            "Salidas",
                            "Registrar merma"
                        )

                    if st.button(
                        "Consultar mermas"
                    ):

                        set_opcion(
                            "Operación Inventarios",
                            "Salidas",
                            "Consultar mermas"
                        )

            # =================================================
            # TRANSFERENCIAS
            # =================================================

            with st.expander("🔁 Transferencias"):

                with st.expander("Almacén"):

                    if st.button(
                        "Transferencia entre almacenes"
                    ):

                        set_opcion(
                            "Operación Inventarios",
                            "Transferencias",
                            "Transferencia entre almacenes"
                        )

                    if st.button(
                        "Consulta transferencias almacén"
                    ):

                        set_opcion(
                            "Operación Inventarios",
                            "Transferencias",
                            "Consulta transferencias almacén"
                        )

                with st.expander("Ubicación"):

                    if st.button(
                        "Transferencia entre ubicaciones"
                    ):

                        set_opcion(
                            "Operación Inventarios",
                            "Transferencias",
                            "Transferencia entre ubicaciones"
                        )

                    if st.button(
                        "Consulta transferencias ubicación"
                    ):

                        set_opcion(
                            "Operación Inventarios",
                            "Transferencias",
                            "Consulta transferencias ubicación"
                        )

        # =================================================
        # OPERACIÓN LOGÍSTICA
        # =================================================

        with st.expander("🚚 Operación Logística"):

            with st.expander("📋 Creación de entregas"):

                if st.button(
                    "🔎 Consulta de pedidos"
                ):

                    set_opcion(
                        "Operación Logística",
                        "Creación de entregas",
                        "Consulta de pedidos"
                    )

                if st.button(
                    "➕ Creación de entregas"
                ):

                    set_opcion(
                        "Operación Logística",
                        "Creación de entregas",
                        "Creación de entregas"
                    )

                if st.button(
                    "🔍 Consulta de entregas"
                ):

                    set_opcion(
                        "Operación Logística",
                        "Creación de entregas",
                        "Consulta de entregas"
                    )

            with st.expander("🚚 Hoja de carga"):

                if st.button(
                    "➕ Creación hoja de carga"
                ):

                    set_opcion(
                        "Operación Logística",
                        "Hoja de carga",
                        "Creación hoja de carga"
                    )

                if st.button(
                    "🔍 Consulta hoja de carga"
                ):

                    set_opcion(
                        "Operación Logística",
                        "Hoja de carga",
                        "Consulta hoja de carga"
                    )

            with st.expander("🚛 Embarques"):

                if st.button(
                    "Confirmar carga embarque"
                ):

                    set_opcion(
                        "Operación Logística",
                        "Embarques",
                        "Embarques"
                    )

                if st.button(
                    "Consultar embarques"
                ):

                    set_opcion(
                        "Operación Logística",
                        "Embarques",
                        "Consultar embarques"
                    )

        # =================================================
        # CONSULTAS Y ANALÍTICOS
        # =================================================

        with st.expander("📊 Consultas y Analíticos"):

            with st.expander("📋 Kardex"):

                if st.button(
                    "Kardex por material"
                ):

                    set_opcion(
                        "Consultas",
                        "Kardex",
                        "Kardex por material"
                    )

                if st.button(
                    "Kardex por almacén"
                ):

                    set_opcion(
                        "Consultas",
                        "Kardex",
                        "Kardex por almacén"
                    )

            with st.expander("🔍 Existencias"):

                if st.button(
                    "Existencias por material"
                ):

                    set_opcion(
                        "Consultas",
                        "Existencias",
                        "Existencias por material"
                    )

                if st.button(
                    "Existencias por almacén"
                ):

                    set_opcion(
                        "Consultas",
                        "Existencias",
                        "Existencias por almacén"
                    )

                if st.button(
                    "Existencias bajo mínimo"
                ):

                    set_opcion(
                        "Consultas",
                        "Existencias",
                        "Existencias bajo mínimo"
                    )

        # =================================================
        # INVENTARIO FÍSICO
        # =================================================

        with st.expander("🧾 Inventario Físico"):

            with st.expander(
                "📌 Conteos cíclicos"
            ):

                if st.button("Crear conteo"):

                    set_opcion(
                        "Inventario Físico",
                        "Conteos cíclicos",
                        "Crear conteo"
                    )

                if st.button(
                    "Capturar conteo"
                ):

                    set_opcion(
                        "Inventario Físico",
                        "Conteos cíclicos",
                        "Capturar conteo"
                    )

                if st.button(
                    "Consultar conteos"
                ):

                    set_opcion(
                        "Inventario Físico",
                        "Conteos cíclicos",
                        "Consultar conteos"
                    )

            with st.expander("✅ Ajustes"):

                if st.button(
                    "Aplicar ajuste"
                ):

                    set_opcion(
                        "Inventario Físico",
                        "Ajustes",
                        "Aplicar ajuste"
                    )

                if st.button(
                    "Consultar ajustes"
                ):

                    set_opcion(
                        "Inventario Físico",
                        "Ajustes",
                        "Consultar ajustes"
                    )

            with st.expander("⚠️ Diferencias"):

                if st.button(
                    "Diferencias por conteo"
                ):

                    set_opcion(
                        "Inventario Físico",
                        "Diferencias",
                        "Diferencias por conteo"
                    )

                if st.button(
                    "Diferencias valorizadas"
                ):

                    set_opcion(
                        "Inventario Físico",
                        "Diferencias",
                        "Diferencias valorizadas"
                    )

    return (
        st.session_state.menu_inv,
        st.session_state.submenu_inv,
        st.session_state.opcion_inv
    )
