
import streamlit as st




def alta_usuario_app():

    

   
    admin_card_open()

    st.markdown("### 📌 Información básica")

    col1, col2, col3 = st.columns(3)

    with col1:
        usuario = st.text_input("Usuario *")

    with col2:
        nombre = st.text_input("Nombre completo *")

    with col3:
        email = st.text_input("Correo electrónico *")

    st.markdown("### 🔐 Seguridad")

    col4, col5, col6 = st.columns(3)

    with col4:
        password = st.text_input("Password temporal *", type="password")

    with col5:
        confirmar_password = st.text_input("Confirmar password *", type="password")

    with col6:
        estado = st.selectbox("Estado", ["Activo", "Inactivo"])

    st.markdown("### 🧩 Acceso")

    col7, col8 = st.columns(2)

    with col7:
        rol = st.selectbox(
            "Rol *",
            [
                "Admin",
                "Gerencia",
                "Compras",
                "Logistica",
                "WMS",
                "Consulta"
            ]
        )

    with col8:
        modulo_inicial = st.selectbox(
            "Módulo inicial",
            [
                "Inicio",
                "Dashboard",
                "Inventarios",
                "Compras",
                "Logistica",
                "Almacen WMS",
                "Mantenimiento"
            ]
        )

    st.divider()

    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 3])

    with col_btn1:
        guardar = st.button("💾 Guardar usuario")

    with col_btn2:
        limpiar = st.button("🔄 Limpiar")

    admin_card_close()

    if limpiar:
        st.rerun()

    if guardar:

        if not usuario or not nombre or not email or not password or not confirmar_password:
            st.warning("⚠️ Completa todos los campos obligatorios.")

        elif password != confirmar_password:
            st.error("❌ Las contraseñas no coinciden.")

        else:
            st.success("✅ Usuario validado correctamente.")

            st.json({
                "usuario": usuario,
                "nombre": nombre,
                "email": email,
                "rol": rol,
                "estado": estado,
                "modulo_inicial": modulo_inicial
            })
