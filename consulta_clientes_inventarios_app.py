import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import sqlite3
from sigem_db import get_db_path


st.set_page_config(
    page_title="SIGEM",
    page_icon="📦",
    layout="wide"
)


st.markdown("""
<style>

.block-container {
    max-width: 1450px;
    padding-top: 1rem;
    padding-left: 2rem;
    padding-right: 2rem;
    padding-bottom: 2rem;
}

div[data-testid="stHorizontalBlock"] {
    gap: 1rem;
}

div[data-testid="stVerticalBlock"] {
    gap: .7rem;
}

.filtros-box {
    border: 1px solid #d9dee8;
    border-radius: 12px;
    padding: 16px;
    background: white;
    margin-bottom: 18px;
}

.mapa-box {
    border: 1px solid #d9dee8;
    border-radius: 12px;
    padding: 16px;
    background: white;
    min-height: 360px;
}

.stTextInput input {
    background-color: #f1f4f8;
    border-radius: 9px;
}

div[data-baseweb="select"] > div {
    background-color: #f1f4f8;
    border-radius: 9px;
}

</style>
""", unsafe_allow_html=True)


def html_card(html, height=220):

    components.html(
        html,
        height=height,
        scrolling=False
    )


def get_conn_inventarios():

    conn = sqlite3.connect(
        get_db_path("logistica")
    )

    conn.row_factory = sqlite3.Row

    return conn


def consulta_clientes_inventarios_app():

    conn = get_conn_inventarios()

    try:

        html_card(
            """
            <div style="
                font-family: Arial;
                background:#f3f6fb;
                padding:10px;
            ">
                <div style="
                    font-size:34px;
                    font-weight:700;
                    color:#111827;
                ">
                    📦 Consulta Clientes - Inventarios
                </div>
                <div style="
                    color:#6b7280;
                    font-size:14px;
                ">
                    Dashboard ejecutivo de clientes para inventarios
                </div>
            </div>
            """,
            height=90
        )

        st.markdown('<div class="filtros-box">', unsafe_allow_html=True)

        f1, f2, f3, f4, f5 = st.columns(5)

        with f1:
            filtro_cliente = st.text_input(
                "🔎 Cliente",
                key="inv_filtro_cliente"
            )

        with f2:
            filtro_ciudad = st.text_input(
                "🏙️ Ciudad",
                key="inv_filtro_ciudad"
            )

        with f3:
            filtro_estado = st.text_input(
                "📍 Estado",
                key="inv_filtro_estado"
            )

        with f4:
            filtro_tipo = st.text_input(
                "🏷️ Tipo cliente",
                key="inv_filtro_tipo"
            )

        with f5:
            filtro_estatus = st.selectbox(
                "📊 Estatus",
                ["Todos", "Activo", "Inactivo"],
                key="inv_filtro_estatus"
            )

        st.markdown('</div>', unsafe_allow_html=True)

        query = """
        SELECT *
        FROM clientes
        WHERE 1=1
        """

        params = []

        if filtro_cliente:
            query += """
            AND (
                nombre_cliente LIKE ?
                OR codigo_cliente LIKE ?
                OR razon_social LIKE ?
            )
            """
            valor = f"%{filtro_cliente}%"
            params.extend([valor, valor, valor])

        if filtro_ciudad:
            query += " AND ciudad LIKE ? "
            params.append(f"%{filtro_ciudad}%")

        if filtro_estado:
            query += " AND estado LIKE ? "
            params.append(f"%{filtro_estado}%")

        if filtro_tipo:
            query += " AND tipo_cliente LIKE ? "
            params.append(f"%{filtro_tipo}%")

        if filtro_estatus != "Todos":
            query += " AND estatus = ? "
            params.append(filtro_estatus)

        query += " ORDER BY nombre_cliente "

        df = pd.read_sql_query(
            query,
            conn,
            params=params
        )

        if df.empty:
            st.warning("No se encontraron clientes.")
            return

        total_activos = len(
            df[
                df["estatus"]
                .astype(str)
                .str.lower()
                .isin(["activo", "activa", "1", "true"])
            ]
        )

        total_criticos = len(
            df[
                df["cliente_critico"]
                .astype(str)
                .str.lower()
                .isin(["si", "sí", "1", "true"])
            ]
        )

        total_servicios = df["nivel_servicio"].nunique()

        k1, k2, k3, k4 = st.columns(4)

        with k1:
            html_card(
                f"""
                <div style="
                    font-family:Arial;
                    background:white;
                    padding:18px;
                    border-radius:18px;
                    box-shadow:0 2px 12px rgba(0,0,0,.08);
                    border-left:6px solid #2563eb;
                    height:96px;
                    box-sizing:border-box;
                ">
                    <div style="font-size:16px;color:#6b7280;">
                        👥 Clientes
                    </div>
                    <div style="font-size:34px;font-weight:bold;color:#2563eb;">
                        {len(df)}
                    </div>
                </div>
                """,
                height=120
            )

        with k2:
            html_card(
                f"""
                <div style="
                    font-family:Arial;
                    background:white;
                    padding:18px;
                    border-radius:18px;
                    box-shadow:0 2px 12px rgba(0,0,0,.08);
                    border-left:6px solid #16a34a;
                    height:96px;
                    box-sizing:border-box;
                ">
                    <div style="font-size:16px;color:#6b7280;">
                        ✅ Activos
                    </div>
                    <div style="font-size:34px;font-weight:bold;color:#16a34a;">
                        {total_activos}
                    </div>
                </div>
                """,
                height=120
            )

        with k3:
            html_card(
                f"""
                <div style="
                    font-family:Arial;
                    background:white;
                    padding:18px;
                    border-radius:18px;
                    box-shadow:0 2px 12px rgba(0,0,0,.08);
                    border-left:6px solid #dc2626;
                    height:96px;
                    box-sizing:border-box;
                ">
                    <div style="font-size:16px;color:#6b7280;">
                        🚨 Críticos
                    </div>
                    <div style="font-size:34px;font-weight:bold;color:#dc2626;">
                        {total_criticos}
                    </div>
                </div>
                """,
                height=120
            )

        with k4:
            html_card(
                f"""
                <div style="
                    font-family:Arial;
                    background:white;
                    padding:18px;
                    border-radius:18px;
                    box-shadow:0 2px 12px rgba(0,0,0,.08);
                    border-left:6px solid #f59e0b;
                    height:96px;
                    box-sizing:border-box;
                ">
                    <div style="font-size:16px;color:#6b7280;">
                        ⭐ Niveles servicio
                    </div>
                    <div style="font-size:34px;font-weight:bold;color:#f59e0b;">
                        {total_servicios}
                    </div>
                </div>
                """,
                height=120
            )

        cliente_select = st.selectbox(
            "🧾 Cliente ejecutivo",
            df["nombre_cliente"].dropna().unique(),
            key="inv_cliente_select"
        )

        cliente = df[
            df["nombre_cliente"] == cliente_select
        ].iloc[0]

        c1, c2, c3 = st.columns([2, 2, 1.2])

        with c1:
            html_card(
                f"""
                <div style="
                    font-family:Arial;
                    background:white;
                    padding:22px;
                    border-radius:18px;
                    box-shadow:0 2px 12px rgba(0,0,0,.08);
                    height:300px;
                    box-sizing:border-box;
                    overflow:hidden;
                ">
                    <div style="font-size:22px;font-weight:bold;margin-bottom:14px;">
                        🧾 PERFIL CLIENTE
                    </div>

                    <span style="
                        display:inline-block;
                        padding:6px 12px;
                        border-radius:20px;
                        background:#dcfce7;
                        color:#166534;
                        font-size:12px;
                        font-weight:bold;
                        margin-right:6px;
                    ">
                        {cliente['estatus']}
                    </span>

                    <span style="
                        display:inline-block;
                        padding:6px 12px;
                        border-radius:20px;
                        background:#fee2e2;
                        color:#991b1b;
                        font-size:12px;
                        font-weight:bold;
                        margin-right:6px;
                    ">
                        Cliente crítico
                    </span>

                    <span style="
                        display:inline-block;
                        padding:6px 12px;
                        border-radius:20px;
                        background:#dbeafe;
                        color:#1d4ed8;
                        font-size:12px;
                        font-weight:bold;
                    ">
                        Inventarios
                    </span>

                    <div style="margin-top:18px;line-height:1.9;font-size:15px;">
                        <b>Código:</b> {cliente['codigo_cliente']}<br>
                        <b>Cliente:</b> {cliente['nombre_cliente']}<br>
                        <b>Razón social:</b> {cliente['razon_social']}<br>
                        <b>RFC:</b> {cliente['rfc']}<br>
                        <b>Tipo cliente:</b> {cliente['tipo_cliente']}<br>
                        <b>Nivel servicio:</b> {cliente['nivel_servicio']}
                    </div>
                </div>
                """,
                height=320
            )

        with c2:
            html_card(
                f"""
                <div style="
                    font-family:Arial;
                    background:white;
                    padding:22px;
                    border-radius:18px;
                    box-shadow:0 2px 12px rgba(0,0,0,.08);
                    height:300px;
                    box-sizing:border-box;
                    overflow:hidden;
                ">
                    <div style="font-size:22px;font-weight:bold;margin-bottom:14px;">
                        📦 INFORMACIÓN INVENTARIOS
                    </div>

                    <div style="line-height:2;font-size:15px;">
                        <b>Ciudad:</b> {cliente['ciudad']}<br>
                        <b>Estado:</b> {cliente['estado']}<br>
                        <b>País:</b> {cliente['pais']}<br>
                        <b>Código postal:</b> {cliente['codigo_postal']}<br>
                        <b>Ruta:</b> {cliente['ruta']}<br>
                        <b>Secuencia ruta:</b> {cliente['secuencia_ruta']}
                    </div>
                </div>
                """,
                height=320
            )

        with c3:
            html_card(
                f"""
                <div style="
                    font-family:Arial;
                    background:white;
                    padding:22px;
                    border-radius:18px;
                    box-shadow:0 2px 12px rgba(0,0,0,.08);
                    height:300px;
                    box-sizing:border-box;
                    overflow:hidden;
                ">
                    <div style="font-size:22px;font-weight:bold;margin-bottom:14px;">
                        ⚠️ ALERTAS
                    </div>

                    <div style="line-height:2;font-size:15px;">
                        <b>Crítico:</b> {cliente['cliente_critico']}<br>
                        <b>Estatus:</b> {cliente['estatus']}<br>
                        <b>Servicio:</b> {cliente['nivel_servicio']}<br>
                        <b>Ruta:</b> {cliente['ruta']}<br>
                        <b>Prioridad:</b> {cliente['prioridad_ruta']}
                    </div>
                </div>
                """,
                height=320
            )

        mapa_col1, mapa_col2 = st.columns([2, 1])

        with mapa_col1:
            st.markdown('<div class="mapa-box">', unsafe_allow_html=True)

            st.subheader("🗺️ Ubicación geográfica cliente")

            df_mapa = pd.DataFrame({
                "lat": [
                    pd.to_numeric(
                        cliente["latitud"],
                        errors="coerce"
                    )
                ],
                "lon": [
                    pd.to_numeric(
                        cliente["longitud"],
                        errors="coerce"
                    )
                ]
            }).dropna()

            if not df_mapa.empty:
                st.map(
                    df_mapa,
                    latitude="lat",
                    longitude="lon",
                    size=250
                )
            else:
                st.info("Cliente sin coordenadas.")

            st.markdown('</div>', unsafe_allow_html=True)

        with mapa_col2:
            html_card(
                f"""
                <div style="
                    font-family:Arial;
                    background:white;
                    padding:22px;
                    border-radius:18px;
                    box-shadow:0 2px 12px rgba(0,0,0,.08);
                    height:360px;
                    box-sizing:border-box;
                    overflow:hidden;
                ">
                    <div style="font-size:22px;font-weight:bold;margin-bottom:14px;">
                        📞 CONTACTO OPERATIVO
                    </div>

                    <div style="line-height:2;font-size:15px;">
                        <b>Contacto:</b> {cliente['contacto_entrega']}<br>
                        <b>Teléfono:</b> {cliente['telefono_contacto']}<br>
                        <b>Correo:</b> {cliente['correo_contacto']}<br>
                        <b>Dirección:</b> {cliente['direccion_entrega']}
                    </div>
                </div>
                """,
                height=380
            )

        tab1, tab2, tab3 = st.tabs([
            "📦 Inventarios",
            "📍 Ubicación",
            "📋 Grid clientes"
        ])


        with tab1:

            st.markdown("### 📦 Simulación Operativa Inventarios")

            sim_col1, sim_col2 = st.columns([2, 1])

            with sim_col1:

                html_card(
                    f"""
                    <div style="
                        background:#ffffff;
                        border-radius:20px;
                        padding:24px;
                        height:420px;
                        box-shadow:0 2px 12px rgba(0,0,0,.08);
                        font-family:Arial;
                        position:relative;
                        overflow:hidden;
                    ">

                        <div style="
                            font-size:24px;
                            font-weight:bold;
                            margin-bottom:18px;
                            color:#111827;
                        ">
                            📦 Simulación Tarima Cliente
                        </div>

                        <div style="
                            position:absolute;
                            left:90px;
                            top:150px;
                            width:240px;
                            height:140px;
                            background:#c08457;
                            border-radius:8px;
                            transform:skew(-12deg);
                            box-shadow:0 12px 18px rgba(0,0,0,.20);
                        "></div>

                        <div style="
                            position:absolute;
                            left:110px;
                            top:90px;
                            width:200px;
                            height:90px;
                            background:#60a5fa;
                            border-radius:10px;
                            box-shadow:0 10px 20px rgba(0,0,0,.15);
                        "></div>

                        <div style="
                            position:absolute;
                            left:350px;
                            top:70px;
                            font-size:16px;
                            color:#374151;
                            line-height:2;
                        ">
                            <b>Tipo:</b> {cliente['tipo_tarima']}<br>
                            <b>Peso máximo:</b> {cliente['peso_max_tarima']}<br>
                            <b>Altura máxima:</b> {cliente['altura_max_tarima']}<br>
                            <b>Servicio:</b> {cliente['nivel_servicio']}
                        </div>

                    </div>
                    """,
                    height=430
                )

            with sim_col2:

                st.metric(
                    "📦 Tipo tarima",
                    cliente["tipo_tarima"]
                )

                st.metric(
                    "⚖️ Peso máximo",
                    cliente["peso_max_tarima"]
                )

                st.metric(
                    "📏 Altura máxima",
                    cliente["altura_max_tarima"]
                )

                st.metric(
                    "📦 Emplaye",
                    cliente["requiere_emplaye"]
                )

                st.metric(
                    "🏷️ Etiqueta",
                    cliente["requiere_etiqueta"]
                )

                st.metric(
                    "📄 Factura",
                    cliente["requiere_factura_impresa"]
                )

                st.metric(
                    "📦 Parcial",
                    cliente["permite_entrega_parcial"]
                )


        with tab2:
            u1, u2, u3 = st.columns(3)

            with u1:
                st.metric("Ciudad", cliente["ciudad"])

            with u2:
                st.metric("Estado", cliente["estado"])

            with u3:
                st.metric("Ruta", cliente["ruta"])

        with tab3:
            columnas = [
                "codigo_cliente",
                "nombre_cliente",
                "razon_social",
                "tipo_cliente",
                "ciudad",
                "estado",
                "ruta",
                "estatus",
                "cliente_critico",
                "nivel_servicio"
            ]

            st.dataframe(
                df[columnas],
                use_container_width=True,
                height=450
            )

            csv = df.to_csv(index=False).encode("utf-8")

            st.download_button(
                "📥 Descargar CSV",
                csv,
                "clientes_inventarios.csv",
                "text/csv"
            )

    except Exception as e:

        st.error(f"Error: {e}")

    finally:

        conn.close()
