import streamlit as st


def sidebar_inventarios():

    with st.sidebar:

        st.markdown("## 🏢 SIGEM")
        st.markdown("### 📦 Inventarios")
        st.markdown("---")

        if "subopcion_inv" not in st.session_state:
            st.session_state.subopcion_inv = "Maestro de productos"

        with st.expander("📘 Maestros", expanded=True):

            with st.expander("📦 Productos", expanded=True):
                if st.button("Maestro de productos"):
                    st.session_state.subopcion_inv = "Maestro de productos"

                if st.button("Clasificaciones"):
                    st.session_state.subopcion_inv = "Clasificaciones"

                if st.button("Atributos"):
                    st.session_state.subopcion_inv = "Atributos"

                if st.button("Códigos de barras"):
                    st.session_state.subopcion_inv = "Códigos de barras"

            with st.expander("📦 Empaques"):
                if st.button("Tipos de empaque"):
                    st.session_state.subopcion_inv = "Tipos de empaque"

                if st.button("Unidades de medida"):
                    st.session_state.subopcion_inv = "Unidades de medida"

            with st.expander("📍 Ubicaciones"):
                if st.button("Almacenes"):
                    st.session_state.subopcion_inv = "Almacenes"

                if st.button("Zonas"):
                    st.session_state.subopcion_inv = "Zonas"

                if st.button("Ubicaciones físicas"):
                    st.session_state.subopcion_inv = "Ubicaciones físicas"

        with st.expander("🔄 Operaciones"):

            with st.expander("📥 Entradas"):
                if st.button("Entrada por compra"):
                    st.session_state.subopcion_inv = "Entrada por compra"

                if st.button("Entrada por ajuste"):
                    st.session_state.subopcion_inv = "Entrada por ajuste"

            with st.expander("📤 Salidas"):
                if st.button("Salida por venta"):
                    st.session_state.subopcion_inv = "Salida por venta"

                if st.button("Salida por merma"):
                    st.session_state.subopcion_inv = "Salida por merma"

            with st.expander("🔁 Transferencias"):
                if st.button("Transferencia almacén"):
                    st.session_state.subopcion_inv = "Transferencia almacén"

                if st.button("Transferencia ubicación"):
                    st.session_state.subopcion_inv = "Transferencia ubicación"

        with st.expander("📊 Consultas"):

            if st.button("Kardex"):
                st.session_state.subopcion_inv = "Kardex"

            if st.button("Existencias"):
                st.session_state.subopcion_inv = "Existencias"

            if st.button("Movimientos"):
                st.session_state.subopcion_inv = "Movimientos"

        with st.expander("🧾 Inventario físico"):

            if st.button("Conteos cíclicos"):
                st.session_state.subopcion_inv = "Conteos cíclicos"

            if st.button("Ajustes"):
                st.session_state.subopcion_inv = "Ajustes"

            if st.button("Diferencias"):
                st.session_state.subopcion_inv = "Diferencias"

    return st.session_state.subopcion_inv
