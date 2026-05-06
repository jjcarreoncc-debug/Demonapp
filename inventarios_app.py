# =========================
# DASHBOARD GENERAL
# =========================
def dashboard_general(df):

    st.title("📊 Dashboard General")

    m = calcular_metricas(df)

    # 🔥 FILA 1
    c1, c2 = st.columns(2)

    with c1:
        card_kpi(
            "📦 Stock Total",
            f"{m['total_stock']:,}",
            "#1f77b4"
        )

    with c2:
        card_kpi(
            "🚨 Críticos",
            m["criticos"],
            "#e74c3c"
        )

    # 🔥 FILA 2
    c3, c4 = st.columns(2)

    with c3:
        card_kpi(
            "⚠️ Sobrestock",
            m["sobrestock"],
            "#f39c12"
        )

    with c4:
        card_kpi(
            "📈 Rotación",
            f"{m['rotacion']:.2f}",
            "#2ecc71"
        )

    # 🔥 FILA 3
    c5, c6 = st.columns(2)

    with c5:
        card_kpi(
            "💰 Ganancia",
            f"${m['ganancia']:,.0f}",
            "#27ae60"
        )

    with c6:
        card_kpi(
            "📊 Productos",
            len(df),
            "#34495e"
        )

    # 🔙 Volver
    if st.button("🔙 Volver"):

        st.session_state.inv_vista = "menu"
        st.rerun()
