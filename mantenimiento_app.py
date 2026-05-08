import streamlit as st
import pandas as pd


# =========================
# APP MANTENIMIENTO
# =========================
def mantenimiento_app():

    st.title("🛠️ Mantenimiento de Usuarios")

    # =========================
    # VALIDACION ROL
    # =========================
    if st.session_state.rol != "Admin":

        st.warning("⛔ No tienes permisos")

        st.stop()

    # =========================
    # DATA MEMORIA
    # =========================
    if "usuarios" not in st.session_state:

        st.session_state.usuarios = [

            {
                "usuario": "admin",
                "nombre": "Administrador",
                "rol": "Admin",
                "estado": "Activo"
            },

            {
                "usuario": "user1",
                "nombre": "Usuario Demo",
                "rol": "Usuario",
                "estado": "Activo"
            }
        ]

    usuarios = st.session_state.usuarios

    # =========================
    # USUARIOS
    # =========================
    st.markdown("### 👥 Usuarios")

    df_users = pd.DataFrame(usuarios)

    st.dataframe(
        df_users,
        use_container_width=True
    )

    # =========================
    # CREAR USUARIO
    # =========================
    st.markdown("### ➕ Crear usuario")

    col1, col2 = st.columns(2)

    with col1:

        nuevo_usuario = st.text_input(
            "Usuario",
            key="u_usuario"
        )

        nombre = st.text_input(
            "Nombre",
            key="u_nombre"
        )

    with col2:

        rol_nuevo = st.selectbox(
            "Rol",
            ["Admin", "Usuario"],
            key="u_rol"
        )

        estado = st.selectbox(
            "Estado",
            ["Activo", "Inactivo"],
            key="u_estado"
        )

    if st.button("Guardar usuario"):

        if nuevo_usuario and nombre:

            usuarios.append({

                "usuario": nuevo_usuario,
                "nombre": nombre,
                "rol": rol_nuevo,
                "estado": estado

            })

            st.success(
                "✅ Usuario creado"
            )

    # =========================
    # ELIMINAR USUARIO
    # =========================
    st.markdown("### ❌ Eliminar usuario")

    lista = [
        u["usuario"]
        for u in usuarios
    ]

    user_del = st.selectbox(
        "Selecciona usuario",
        lista,
        key="del_user"
    )

    if st.button("Eliminar usuario"):

        st.session_state.usuarios = [

            u for u in usuarios
            if u["usuario"] != user_del

        ]

        st.success(
            "🗑️ Usuario eliminado"
        )
