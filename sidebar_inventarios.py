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
            set_opcion("Maestros", "Productos", "Maestro de materiales")

        # =========================
        # MAESTROS
        # =========================
        with st.expander("📘 Maestros", expanded=True):

            with st.expander("📦 Productos", expanded=True):
                #
                with st.expander("📋 Maestro de materiales", expanded=True):

                    if st.button("➕ Alta de material"):
                        set_opcion("Maestros", "Productos", "Alta de material")
                
                    if st.button("❌ Baja de material"):
                        set_opcion("Maestros", "Productos", "Baja de material")
                
                    if st.button("🔍 Consulta de material"):
                        set_opcion("Maestros", "Productos", "Consulta de material")

        
                with st.expander("🏷️ Clasificaciones"):
                    if st.button("Categorías"):
                        set_opcion("Maestros", "Productos", "Categorías")
                    if st.button("Familias"):
                        set_opcion("Maestros", "Productos", "Familias")
                    if st.button("Marcas"):
                        set_opcion("Maestros", "Productos", "Marcas")

                with st.expander("🔢 Códigos"):
                    if st.button("Códigos de barras"):
                        set_opcion("Maestros", "Productos", "Códigos de barras")
                    if st.button("SKU alternos"):
                        set_opcion("Maestros", "Productos", "SKU alternos")

            with st.expander("📦 Empaques"):

                with st.expander("📏 Unidades"):
                    if st.button("Alta unidad"):
                        set_opcion("Maestros", "Empaques", "Alta unidad")
                    if st.button("Consulta unidades"):
                        set_opcion("Maestros", "Empaques", "Consulta unidades")

                with st.expander("📦 Tipos de empaque"):
                    if st.button("Alta empaque"):
                        set_opcion("Maestros", "Empaques", "Alta empaque")
                    if st.button("Consulta empaques"):
                        set_opcion("Maestros", "Empaques", "Consulta empaques")

            with st.expander("📍 Ubicaciones"):

                with st.expander("🏬 Almacenes"):
                    if st.button("Alta almacén"):
                        set_opcion("Maestros", "Ubicaciones", "Alta almacén")
                    if st.button("Consulta almacenes"):
                        set_opcion("Maestros", "Ubicaciones", "Consulta almacenes")

                with st.expander("🧭 Zonas"):
                    if st.button("Alta zona"):
                        set_opcion("Maestros", "Ubicaciones", "Alta zona")
                    if st.button("Consulta zonas"):
                        set_opcion("Maestros", "Ubicaciones", "Consulta zonas")

                with st.expander("📌 Ubicaciones físicas"):
                    if st.button("Alta ubicación"):
                        set_opcion("Maestros", "Ubicaciones", "Alta ubicación")
                    if st.button("Consulta ubicaciones"):
                        set_opcion("Maestros", "Ubicaciones", "Consulta ubicaciones")

        # =========================
        # OPERACIONES
        # =========================
        with st.expander("🔄 Operaciones"):

            with st.expander("📥 Entradas"):

                with st.expander("Compra"):
                    if st.button("Registrar entrada compra"):
                        set_opcion("Operaciones", "Entradas", "Registrar entrada compra")
                    if st.button("Consultar entradas compra"):
                        set_opcion("Operaciones", "Entradas", "Consultar entradas compra")

                with st.expander("Ajuste"):
                    if st.button("Registrar entrada ajuste"):
                        set_opcion("Operaciones", "Entradas", "Registrar entrada ajuste")
                    if st.button("Consultar entradas ajuste"):
                        set_opcion("Operaciones", "Entradas", "Consultar entradas ajuste")

            with st.expander("📤 Salidas"):

                with st.expander("Venta"):
                    if st.button("Registrar salida venta"):
                        set_opcion("Operaciones", "Salidas", "Registrar salida venta")
                    if st.button("Consultar salidas venta"):
                        set_opcion("Operaciones", "Salidas", "Consultar salidas venta")

                with st.expander("Merma"):
                    if st.button("Registrar merma"):
                        set_opcion("Operaciones", "Salidas", "Registrar merma")
                    if st.button("Consultar mermas"):
                        set_opcion("Operaciones", "Salidas", "Consultar mermas")

            with st.expander("🔁 Transferencias"):

                with st.expander("Almacén"):
                    if st.button("Transferencia entre almacenes"):
                        set_opcion("Operaciones", "Transferencias", "Transferencia entre almacenes")
                    if st.button("Consulta transferencias almacén"):
                        set_opcion("Operaciones", "Transferencias", "Consulta transferencias almacén")

                with st.expander("Ubicación"):
                    if st.button("Transferencia entre ubicaciones"):
                        set_opcion("Operaciones", "Transferencias", "Transferencia entre ubicaciones")
                    if st.button("Consulta transferencias ubicación"):
                        set_opcion("Operaciones", "Transferencias", "Consulta transferencias ubicación")

        # =========================
        # CONSULTAS
        # =========================
        with st.expander("📊 Consultas"):

            with st.expander("📋 Kardex"):
                if st.button("Kardex por material"):
                    set_opcion("Consultas", "Kardex", "Kardex por material")
                if st.button("Kardex por almacén"):
                    set_opcion("Consultas", "Kardex", "Kardex por almacén")

            with st.expander("🔍 Existencias"):
                if st.button("Existencias por material"):
                    set_opcion("Consultas", "Existencias", "Existencias por material")
                if st.button("Existencias por almacén"):
                    set_opcion("Consultas", "Existencias", "Existencias por almacén")
                if st.button("Existencias bajo mínimo"):
                    set_opcion("Consultas", "Existencias", "Existencias bajo mínimo")

        # =========================
        # INVENTARIO FÍSICO
        # =========================
        with st.expander("🧾 Inventario físico"):

            with st.expander("📌 Conteos cíclicos"):
                if st.button("Crear conteo"):
                    set_opcion("Inventario físico", "Conteos cíclicos", "Crear conteo")
                if st.button("Capturar conteo"):
                    set_opcion("Inventario físico", "Conteos cíclicos", "Capturar conteo")
                if st.button("Consultar conteos"):
                    set_opcion("Inventario físico", "Conteos cíclicos", "Consultar conteos")

            with st.expander("✅ Ajustes"):
                if st.button("Aplicar ajuste"):
                    set_opcion("Inventario físico", "Ajustes", "Aplicar ajuste")
                if st.button("Consultar ajustes"):
                    set_opcion("Inventario físico", "Ajustes", "Consultar ajustes")

            with st.expander("⚠️ Diferencias"):
                if st.button("Diferencias por conteo"):
                    set_opcion("Inventario físico", "Diferencias", "Diferencias por conteo")
                if st.button("Diferencias valorizadas"):
                    set_opcion("Inventario físico", "Diferencias", "Diferencias valorizadas")

    return (
        st.session_state.menu_inv,
        st.session_state.submenu_inv,
        st.session_state.opcion_inv
    )
