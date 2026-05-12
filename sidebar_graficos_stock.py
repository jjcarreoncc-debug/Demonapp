import streamlit as st


def sidebar_graficos_stock():

    st.sidebar.markdown("## 📊 Gráficos de Stock")

    menu = None

    if st.sidebar.button(
        "🏠 Inicio",
        use_container_width=True
    ):
        menu = "inicio"

    if st.sidebar.button(
        "📊 Dashboard general",
        use_container_width=True
    ):
        menu = "dashboard"

    if st.sidebar.button(
        "🚨 Críticos",
        use_container_width=True
    ):
        menu = "criticos"

    if st.sidebar.button(
        "⚠️ Sobrestock",
        use_container_width=True
    ):
        menu = "sobrestock"

    if st.sidebar.button(
        "🔄 Rotación",
        use_container_width=True
    ):
        menu = "rotacion"

    if st.sidebar.button(
        "🤖 IA",
        use_container_width=True
    ):
        menu = "ia"

    return menu
