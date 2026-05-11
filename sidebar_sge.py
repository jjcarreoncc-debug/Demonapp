
import streamlit as st


def sidebar_sge():

    if "transaccion_sge" not in st.session_state:
        st.session_state.transaccion_sge = (
            "SGE-IN-MA-CO-003"
        )

    with st.sidebar:

        st.title("🏢 SIGEM")

        st.markdown("---")

        # =====================================
        # OPERACIÓN
        # =====================================

        with st.expander(
            "🏭 Operación",
            expanded=True
        ):

            # =====================================
            # ENTRADAS
            # =====================================

            with st.expander(
                "📥 Entradas",
                expanded=True
            ):

                with st.expander(
                    "🛒 Compra",
                    expanded=False
                ):

                    if st.button(
                        "SGE-CO-EN-RE-001 Registrar entrada compra"
                    ):
                        st.session_state.transaccion_sge = (
                            "SGE-CO-EN-RE-001"
                        )

                    if st.button(
                        "SGE-CO-EN-CO-002 Consultar entradas compra"
                    ):
                        st.session_state.transaccion_sge = (
                            "SGE-CO-EN-CO-002"
                        )

                with st.expander(
                    "⚖️ Ajuste",
                    expanded=False
                ):

                    if st.button(
                        "SGE-IN-AJ-RE-001 Registrar ajuste inventario"
                    ):
                        st.session_state.transaccion_sge = (
                            "SGE-IN-AJ-RE-001"
                        )

            # =====================================
            # INVENTARIOS
            # =====================================

            with st.expander(
                "📦 Inventarios",
                expanded=True
            ):

                # =====================================
                # DATOS MAESTROS
                # =====================================

                with st.expander(
                    "📘 Datos Maestros",
                    expanded=True
                ):

                    st.markdown("### Materiales")

                    if st.button(
                        "SGE-IN-MA-AL-001 Alta materiales"
                    ):
                        st.session_state.transaccion_sge = (
                            "SGE-IN-MA-AL-001"
                        )

                    if st.button(
                        "SGE-IN-MA-MO-002 Modificación materiales"
                    ):
                        st.session_state.transaccion_sge = (
                            "SGE-IN-MA-MO-002"
                        )

                    if st.button(
                        "SGE-IN-MA-CO-003 Consulta materiales"
                    ):
                        st.session_state.transaccion_sge = (
                            "SGE-IN-MA-CO-003"
                        )

                    if st.button(
                        "SGE-IN-MA-BA-004 Baja materiales"
                    ):
                        st.session_state.transaccion_sge = (
                            "SGE-IN-MA-BA-004"
                        )

                    st.markdown("---")

                    st.markdown("### Segmentos")

                    if st.button(
                        "SGE-IN-SE-AL-005 Alta segmentos"
                    ):
                        st.session_state.transaccion_sge = (
                            "SGE-IN-SE-AL-005"
                        )

                    if st.button(
                        "SGE-IN-SE-MO-006 Modificación segmentos"
                    ):
                        st.session_state.transaccion_sge = (
                            "SGE-IN-SE-MO-006"
                        )

                    if st.button(
                        "SGE-IN-SE-CO-007 Consulta segmentos"
                    ):
                        st.session_state.transaccion_sge = (
                            "SGE-IN-SE-CO-007"
                        )

                    if st.button(
                        "SGE-IN-SE-BA-008 Baja segmentos"
                    ):
                        st.session_state.transaccion_sge = (
                            "SGE-IN-SE-BA-008"
                        )

                    st.markdown("---")

                    st.markdown("### Empaques")

                    if st.button(
                        "SGE-IN-EM-AL-009 Alta empaques"
                    ):
                        st.session_state.transaccion_sge = (
                            "SGE-IN-EM-AL-009"
                        )

                    if st.button(
                        "SGE-IN-EM-MO-010 Modificación empaques"
                    ):
                        st.session_state.transaccion_sge = (
                            "SGE-IN-EM-MO-010"
                        )

                    if st.button(
                        "SGE-IN-EM-CO-011 Consulta empaques"
                    ):
                        st.session_state.transaccion_sge = (
                            "SGE-IN-EM-CO-011"
                        )

                    if st.button(
                        "SGE-IN-EM-BA-012 Baja empaques"
                    ):
                        st.session_state.transaccion_sge = (
                            "SGE-IN-EM-BA-012"
                        )

    return st.session_state.transaccion_sge
