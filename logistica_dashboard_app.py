  import streamlit as st
  from logistica_dashboard_app import dashboard_logistica

# =========================
# DASHBOARD LOGÍSTICA
# =========================
def dashboard_logistica(
    transito,
    bodegas,
    transportistas
):

    st.title("🚚 Dashboard Ejecutivo Logística")

    # =========================
    # VALIDACIÓN
    # =========================
    if "ESTADO_TRANSITO" not in transito.columns:
        transito["ESTADO_TRANSITO"] = "EN_TRANSITO"

    # =========================
    # KPIs
    # =========================
    total_transitos = len(transito)

    total_bodegas = (
        bodegas["ID_BODEGA"].nunique()
    )

    total_transportistas = (
        transportistas["ID_TRANSPORTISTA"].nunique()
    )

    unidades_transito = int(
        transito["CANTIDAD"].sum()
    )

    en_transito = transito[
        transito["ESTADO_TRANSITO"]
        .astype(str)
        .str.upper() == "EN_TRANSITO"
    ]

    retrasados = transito[
        transito["ESTADO_TRANSITO"]
        .astype(str)
        .str.upper() == "RETRASADO"
    ]

    recibidos = transito[
        transito["ESTADO_TRANSITO"]
        .astype(str)
        .str.upper() == "RECIBIDO"
    ]

    estado_resumen = (
        transito["ESTADO_TRANSITO"]
        .value_counts()
        .reset_index()
    )

    estado_resumen.columns = [
        "ESTADO_TRANSITO",
        "TOTAL"
    ]

    # =========================
    # TABS
    # =========================
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Resumen",
        "Tránsito",
        "Bodegas",
        "Transportistas",
        "Riesgos",
        "Detalle"
    ])

    # =========================
    # RESUMEN
    # =========================
    with tab1:

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric(
                "🚛 Tránsitos",
                total_transitos
            )

        with c2:
            st.metric(
                "📦 Unidades Movimiento",
                f"{unidades_transito:,}"
            )

        with c3:
            st.metric(
                "🏬 Bodegas",
                total_bodegas
            )

        with c4:
            st.metric(
                "🚚 Transportistas",
                total_transportistas
            )

        c5, c6, c7 = st.columns(3)

        with c5:
            st.metric(
                "🟡 En Tránsito",
                len(en_transito)
            )

        with c6:
            st.metric(
                "🔴 Retrasados",
                len(retrasados)
            )

        with c7:
            st.metric(
                "🟢 Recibidos",
                len(recibidos)
            )

    # =========================
    # TRANSITO
    # =========================
    with tab2:

        st.subheader("🚛 Estado Tránsitos")

        st.bar_chart(
            estado_resumen.set_index(
                "ESTADO_TRANSITO"
            )["TOTAL"]
        )

        st.dataframe(
            transito,
            use_container_width=True
        )

    # =========================
    # BODEGAS
    # =========================
    with tab3:

        st.subheader("🏬 Bodegas")

        st.dataframe(
            bodegas,
            use_container_width=True
        )

    # =========================
    # TRANSPORTISTAS
    # =========================
    with tab4:

        st.subheader("🚚 Transportistas")

        st.dataframe(
            transportistas,
            use_container_width=True
        )

    # =========================
    # RIESGOS
    # =========================
    with tab5:

        st.subheader("🚨 Riesgos Logísticos")

        st.metric(
            "🔴 Retrasados",
            len(retrasados)
        )

        st.dataframe(
            retrasados,
            use_container_width=True
        )

    # =========================
    # DETALLE
    # =========================
    with tab6:

        st.subheader("📋 Detalle General")

        st.dataframe(
            transito,
            use_container_width=True
        )
