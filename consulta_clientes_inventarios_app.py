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

            tipo_tarima = cliente.get("tipo_tarima", "")
            peso_max_tarima = cliente.get("peso_max_tarima", "")
            altura_max_tarima = cliente.get("altura_max_tarima", "")
            requiere_emplaye = cliente.get("requiere_emplaye", "")
            requiere_etiqueta = cliente.get("requiere_etiqueta", "")
            requiere_factura = cliente.get("requiere_factura_impresa", "")
            permite_parcial = cliente.get("permite_entrega_parcial", "")
            nivel_servicio = cliente.get("nivel_servicio", "")
            cliente_critico = cliente.get("cliente_critico", "")
            estatus_cliente = cliente.get("estatus", "")

            html_card(
                f"""
                <div style="
                    font-family:Arial, sans-serif;
                    background:#ffffff;
                    border-radius:22px;
                    padding:22px;
                    box-sizing:border-box;
                    width:100%;
                    height:720px;
                    overflow:hidden;
                ">

                    <div style="
                        display:flex;
                        align-items:center;
                        justify-content:space-between;
                        margin-bottom:18px;
                    ">
                        <div>
                            <div style="
                                font-size:26px;
                                font-weight:800;
                                color:#111827;
                                margin-bottom:4px;
                            ">
                                📦 Simulación 3D de restricciones de cliente
                            </div>
                            <div style="
                                font-size:15px;
                                color:#6b7280;
                            ">
                                Visualización de capacidades y requerimientos operativos de inventarios
                            </div>
                        </div>

                        <div style="
                            display:flex;
                            gap:10px;
                            align-items:center;
                        ">
                            <div style="
                                border:1px solid #d9dee8;
                                border-radius:12px;
                                padding:12px 18px;
                                font-size:14px;
                                font-weight:700;
                                color:#111827;
                                background:#ffffff;
                            ">
                                🧊 Vista 3D
                            </div>
                            <div style="
                                border:1px solid #d9dee8;
                                border-radius:12px;
                                padding:12px 18px;
                                font-size:14px;
                                font-weight:700;
                                color:#111827;
                                background:#ffffff;
                            ">
                                🔄 Valores del cliente
                            </div>
                        </div>
                    </div>

                    <div style="
                        display:grid;
                        grid-template-columns: 2.1fr 1fr;
                        gap:18px;
                        height:610px;
                    ">

                        <div style="
                            position:relative;
                            border-radius:18px;
                            overflow:hidden;
                            background:
                                linear-gradient(120deg, rgba(17,24,39,.78), rgba(55,65,81,.38)),
                                linear-gradient(180deg, #e5e7eb 0%, #d1d5db 45%, #9ca3af 100%);
                            box-shadow:0 2px 14px rgba(0,0,0,.12);
                        ">

                            <div style="
                                position:absolute;
                                left:0;
                                right:0;
                                bottom:0;
                                height:220px;
                                background:
                                    linear-gradient(135deg, transparent 0 48%, rgba(255,255,255,.18) 49% 51%, transparent 52%),
                                    linear-gradient(45deg, transparent 0 48%, rgba(255,255,255,.14) 49% 51%, transparent 52%),
                                    #6b7280;
                                background-size:90px 90px;
                                clip-path:polygon(0 30%, 100% 0, 100% 100%, 0 100%);
                                opacity:.65;
                            "></div>

                            <div style="
                                position:absolute;
                                left:24px;
                                top:24px;
                                width:285px;
                                background:rgba(17,24,39,.82);
                                color:white;
                                border-radius:14px;
                                padding:18px 20px;
                                box-sizing:border-box;
                                box-shadow:0 8px 22px rgba(0,0,0,.25);
                            ">
                                <div style="
                                    font-size:17px;
                                    font-weight:800;
                                    margin-bottom:12px;
                                ">
                                    Especificaciones de tarima
                                </div>

                                <div style="display:grid;grid-template-columns:1fr 1fr;border-top:1px solid rgba(255,255,255,.15);padding:10px 0;font-size:14px;">
                                    <div>Tipo tarima</div>
                                    <div style="font-weight:800;color:#93c5fd;text-align:right;">{tipo_tarima}</div>
                                </div>
                                <div style="display:grid;grid-template-columns:1fr 1fr;border-top:1px solid rgba(255,255,255,.15);padding:10px 0;font-size:14px;">
                                    <div>Peso máximo</div>
                                    <div style="font-weight:800;color:#86efac;text-align:right;">{peso_max_tarima}</div>
                                </div>
                                <div style="display:grid;grid-template-columns:1fr 1fr;border-top:1px solid rgba(255,255,255,.15);padding:10px 0;font-size:14px;">
                                    <div>Altura máxima</div>
                                    <div style="font-weight:800;color:#7dd3fc;text-align:right;">{altura_max_tarima}</div>
                                </div>
                                <div style="display:grid;grid-template-columns:1fr 1fr;border-top:1px solid rgba(255,255,255,.15);padding:10px 0 0 0;font-size:14px;">
                                    <div>Nivel servicio</div>
                                    <div style="font-weight:800;color:#fde68a;text-align:right;">{nivel_servicio}</div>
                                </div>
                            </div>

                            <div style="
                                position:absolute;
                                left:342px;
                                top:98px;
                                width:380px;
                                height:340px;
                                transform:perspective(900px) rotateX(56deg) rotateZ(-37deg);
                                transform-style:preserve-3d;
                            ">
                                <div style="
                                    position:absolute;
                                    width:340px;
                                    height:260px;
                                    background:linear-gradient(145deg,#b7793f,#d19a62);
                                    border-radius:10px;
                                    box-shadow:0 35px 40px rgba(0,0,0,.35);
                                    transform:translateZ(0px);
                                "></div>

                                <div style="
                                    position:absolute;
                                    left:18px;
                                    top:-125px;
                                    width:300px;
                                    height:230px;
                                    background:
                                        repeating-linear-gradient(90deg, rgba(255,255,255,.22) 0 2px, transparent 2px 42px),
                                        repeating-linear-gradient(0deg, rgba(0,0,0,.10) 0 2px, transparent 2px 42px),
                                        linear-gradient(145deg,#a56b38,#c48a4f);
                                    border-radius:10px;
                                    box-shadow:0 18px 25px rgba(0,0,0,.28);
                                    transform:translateZ(120px);
                                "></div>

                                <div style="
                                    position:absolute;
                                    left:18px;
                                    top:-125px;
                                    width:300px;
                                    height:230px;
                                    background:repeating-linear-gradient(0deg, rgba(255,255,255,.26) 0 3px, transparent 3px 18px);
                                    border-radius:10px;
                                    opacity:.48;
                                    transform:translateZ(122px);
                                "></div>

                                <div style="
                                    position:absolute;
                                    left:35px;
                                    top:120px;
                                    width:55px;
                                    height:36px;
                                    background:#8b5a2b;
                                    border-radius:4px;
                                    transform:translateZ(12px);
                                "></div>
                                <div style="
                                    position:absolute;
                                    left:140px;
                                    top:142px;
                                    width:55px;
                                    height:36px;
                                    background:#8b5a2b;
                                    border-radius:4px;
                                    transform:translateZ(12px);
                                "></div>
                                <div style="
                                    position:absolute;
                                    left:245px;
                                    top:165px;
                                    width:55px;
                                    height:36px;
                                    background:#8b5a2b;
                                    border-radius:4px;
                                    transform:translateZ(12px);
                                "></div>
                            </div>

                            <div style="
                                position:absolute;
                                left:280px;
                                bottom:92px;
                                width:235px;
                                height:5px;
                                background:#22c55e;
                                transform:rotate(15deg);
                                border-radius:99px;
                                box-shadow:0 0 10px rgba(34,197,94,.45);
                            "></div>
                            <div style="
                                position:absolute;
                                left:298px;
                                bottom:65px;
                                background:rgba(17,24,39,.82);
                                color:white;
                                border-radius:10px;
                                padding:10px 16px;
                                text-align:center;
                                font-size:14px;
                                box-shadow:0 6px 16px rgba(0,0,0,.25);
                            ">
                                Largo<br><b style="font-size:20px;">Tarima</b>
                            </div>

                            <div style="
                                position:absolute;
                                left:535px;
                                bottom:92px;
                                width:205px;
                                height:5px;
                                background:#ef4444;
                                transform:rotate(-25deg);
                                border-radius:99px;
                                box-shadow:0 0 10px rgba(239,68,68,.45);
                            "></div>
                            <div style="
                                position:absolute;
                                left:640px;
                                bottom:65px;
                                background:rgba(17,24,39,.82);
                                color:white;
                                border-radius:10px;
                                padding:10px 16px;
                                text-align:center;
                                font-size:14px;
                                box-shadow:0 6px 16px rgba(0,0,0,.25);
                            ">
                                Ancho<br><b style="font-size:20px;">Tarima</b>
                            </div>

                            <div style="
                                position:absolute;
                                left:760px;
                                top:130px;
                                width:5px;
                                height:260px;
                                background:#3b82f6;
                                border-radius:99px;
                                box-shadow:0 0 10px rgba(59,130,246,.45);
                            "></div>
                            <div style="
                                position:absolute;
                                left:790px;
                                top:250px;
                                background:rgba(17,24,39,.82);
                                color:white;
                                border-radius:10px;
                                padding:10px 16px;
                                font-size:14px;
                                box-shadow:0 6px 16px rgba(0,0,0,.25);
                            ">
                                Altura máx.<br><b style="font-size:20px;">{altura_max_tarima}</b>
                            </div>

                            <div style="
                                position:absolute;
                                left:24px;
                                bottom:24px;
                                width:190px;
                                background:rgba(17,24,39,.82);
                                color:white;
                                border-radius:14px;
                                padding:16px 18px;
                                box-sizing:border-box;
                                box-shadow:0 8px 22px rgba(0,0,0,.25);
                            ">
                                <div style="font-size:17px;font-weight:800;margin-bottom:14px;">Vista 3D</div>
                                <div style="font-size:14px;line-height:2.1;">
                                    🖱️ Arrastrar para rotar<br>
                                    🔍 Scroll para acercar<br>
                                    ✥ Click derecho para mover
                                </div>
                            </div>

                            <div style="
                                position:absolute;
                                left:240px;
                                right:24px;
                                bottom:24px;
                                display:grid;
                                grid-template-columns:repeat(4,1fr);
                                gap:10px;
                            ">
                                <div style="background:rgba(17,24,39,.78);color:white;border-radius:12px;padding:10px;text-align:center;border:2px solid #3b82f6;">📦<br>Frontal</div>
                                <div style="background:rgba(17,24,39,.78);color:white;border-radius:12px;padding:10px;text-align:center;">📦<br>Lateral</div>
                                <div style="background:rgba(17,24,39,.78);color:white;border-radius:12px;padding:10px;text-align:center;">▦<br>Superior</div>
                                <div style="background:rgba(17,24,39,.78);color:white;border-radius:12px;padding:10px;text-align:center;">🧊<br>Perspectiva</div>
                            </div>
                        </div>

                        <div style="
                            display:grid;
                            grid-template-rows:auto auto auto;
                            gap:14px;
                        ">

                            <div style="
                                background:#ffffff;
                                border:1px solid #e5e7eb;
                                border-radius:18px;
                                padding:18px;
                                box-shadow:0 2px 12px rgba(0,0,0,.08);
                            ">
                                <div style="
                                    font-size:18px;
                                    font-weight:800;
                                    color:#111827;
                                    margin-bottom:16px;
                                ">
                                    Resumen de capacidades
                                </div>

                                <div style="
                                    display:grid;
                                    grid-template-columns:1fr 1fr 1fr;
                                    gap:10px;
                                ">
                                    <div style="border:1px solid #ddd6fe;border-radius:12px;padding:14px;text-align:center;">
                                        <div style="font-size:30px;">⚖️</div>
                                        <div style="font-size:13px;color:#1f2937;margin-top:8px;">Peso máximo</div>
                                        <div style="font-size:21px;font-weight:800;color:#6d28d9;margin-top:6px;">{peso_max_tarima}</div>
                                    </div>

                                    <div style="border:1px solid #dbeafe;border-radius:12px;padding:14px;text-align:center;">
                                        <div style="font-size:30px;">↕️</div>
                                        <div style="font-size:13px;color:#1f2937;margin-top:8px;">Altura máxima</div>
                                        <div style="font-size:21px;font-weight:800;color:#2563eb;margin-top:6px;">{altura_max_tarima}</div>
                                    </div>

                                    <div style="border:1px solid #dcfce7;border-radius:12px;padding:14px;text-align:center;">
                                        <div style="font-size:30px;">▦</div>
                                        <div style="font-size:13px;color:#1f2937;margin-top:8px;">Tipo tarima</div>
                                        <div style="font-size:19px;font-weight:800;color:#15803d;margin-top:6px;">{tipo_tarima}</div>
                                    </div>
                                </div>
                            </div>

                            <div style="
                                background:#ffffff;
                                border:1px solid #e5e7eb;
                                border-radius:18px;
                                padding:18px;
                                box-shadow:0 2px 12px rgba(0,0,0,.08);
                            ">
                                <div style="
                                    font-size:18px;
                                    font-weight:800;
                                    color:#111827;
                                    margin-bottom:14px;
                                ">
                                    Requerimientos operativos
                                </div>

                                <div style="display:grid;gap:9px;">
                                    <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #e5e7eb;padding:8px 0;">
                                        <span>🧻 Requiere emplaye</span>
                                        <b style="background:#dcfce7;color:#166534;border-radius:10px;padding:5px 14px;">{requiere_emplaye}</b>
                                    </div>
                                    <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #e5e7eb;padding:8px 0;">
                                        <span>🏷️ Requiere etiqueta</span>
                                        <b style="background:#dbeafe;color:#1d4ed8;border-radius:10px;padding:5px 14px;">{requiere_etiqueta}</b>
                                    </div>
                                    <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #e5e7eb;padding:8px 0;">
                                        <span>📄 Requiere factura impresa</span>
                                        <b style="background:#ffedd5;color:#9a3412;border-radius:10px;padding:5px 14px;">{requiere_factura}</b>
                                    </div>
                                    <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;">
                                        <span>📦 Permite entrega parcial</span>
                                        <b style="background:#dcfce7;color:#166534;border-radius:10px;padding:5px 14px;">{permite_parcial}</b>
                                    </div>
                                </div>
                            </div>

                            <div style="
                                background:#ffffff;
                                border:1px solid #e5e7eb;
                                border-radius:18px;
                                padding:18px;
                                box-shadow:0 2px 12px rgba(0,0,0,.08);
                            ">
                                <div style="
                                    font-size:18px;
                                    font-weight:800;
                                    color:#111827;
                                    margin-bottom:12px;
                                ">
                                    Información adicional
                                </div>

                                <div style="display:grid;gap:10px;font-size:15px;">
                                    <div style="display:flex;justify-content:space-between;">
                                        <span>Nivel de servicio</span>
                                        <b style="color:#f59e0b;">{nivel_servicio}</b>
                                    </div>
                                    <div style="display:flex;justify-content:space-between;">
                                        <span>Cliente crítico</span>
                                        <b style="background:#fee2e2;color:#991b1b;border-radius:10px;padding:4px 12px;">{cliente_critico}</b>
                                    </div>
                                    <div style="display:flex;justify-content:space-between;">
                                        <span>Estatus</span>
                                        <b style="background:#dcfce7;color:#166534;border-radius:10px;padding:4px 12px;">{estatus_cliente}</b>
                                    </div>
                                </div>
                            </div>

                        </div>

                    </div>

                    <div style="
                        margin-top:14px;
                        background:#eff6ff;
                        border:1px solid #bfdbfe;
                        color:#1e3a8a;
                        border-radius:12px;
                        padding:12px 16px;
                        font-size:14px;
                    ">
                        ℹ️ Nota: la simulación toma los valores registrados del cliente seleccionado en la base de datos.
                    </div>

                </div>
                """,
                height=760
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
