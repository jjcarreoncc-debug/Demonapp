
import streamlit as st


def baja_material_app():

    st.title("❌ Baja de material")

    st.caption(
        "Maestros / Productos / Maestro de materiales / Baja de material"
    )

    with st.form("form_baja_material"):

        # =========================
        # IDENTIFICACION
        # =========================
        st.subheader("📋 Identificación del material")

        c1, c2 = st.columns(2)

        with c1:

            codigo_material = st.text_input(
                "Código material"
            )

            descripcion = st.text_input(
                "Descripción material"
            )

        with c2:

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

            estatus_actual = st.selectbox(
                "Estatus actual",
                [
                    "Activo",
                    "Bloqueado",
                    "Descontinuado"
                ]
            )

        # =========================
        # MOTIVO BAJA
        # =========================
        st.markdown("---")
        st.subheader("⚠️ Motivo de baja")

        c1, c2 = st.columns(2)

        with c1:

            motivo_baja = st.selectbox(
                "Motivo",
                [
                    "Descontinuado",
                    "Duplicado",
                    "Error de creación",
                    "Obsoleto",
                    "Fin de vida",
                    "Otro"
                ]
            )

            fecha_baja = st.date_input(
                "Fecha baja"
            )

        with c2:

            bloquear_compras = st.checkbox(
                "Bloquear compras"
            )

            bloquear_ventas = st.checkbox(
                "Bloquear ventas"
            )

            bloquear_movimientos = st.checkbox(
                "Bloquear movimientos inventario"
            )

        comentarios = st.text_area(
            "Comentarios"
        )

        # =========================
        # VALIDACIONES
        # =========================
        st.markdown("---")
        st.subheader("🔎 Validaciones")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric("Existencia actual", "125")

        with c2:
            st.metric("Órdenes abiertas", "3")

        with c3:
            st.metric("SKUs asociados", "12")

        validar = st.checkbox(
            "Confirmo que revisé dependencias del material"
        )

        st.markdown("---")

        aplicar_baja = st.form_submit_button(
            "❌ Aplicar baja material"
        )

        if aplicar_baja:

            if not validar:

                st.error(
                    "Debe confirmar validaciones."
                )

            else:

                st.success(
                    "✅ Baja de material aplicada correctamente."
                )

                st.write({
                    "codigo_material": codigo_material,
                    "motivo_baja": motivo_baja,
                    "fecha_baja": str(fecha_baja),
                    "bloquear_compras": bloquear_compras,
                    "bloquear_ventas": bloquear_ventas,
                    "bloquear_movimientos": bloquear_movimientos
                })
