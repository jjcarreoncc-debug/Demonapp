import streamlit as st
import pandas as pd
import sqlite3
import textwrap
from sigem_db import get_db_path


# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="SIGEM",
    page_icon="🚚",
    layout="wide"
)


# =========================================================
# FUNCION HTML
# =========================================================

def html_card(html):

    st.markdown(
        textwrap.dedent(html),
        unsafe_allow_html=True
    )


# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

/* =========================
FONDO GENERAL
========================= */

.stApp {
    background-color: #f3f6fb;
}

/* =========================
TITULOS
========================= */

.main-title {
    font-size: 34px;
    font-weight: 700;
    color: #111827;
}

.sub-title {
    color: #6b7280;
    font-size: 14px;
    margin-bottom: 20px;
}

/* =========================
CARDS
========================= */

.card {
    background: white;
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    margin-bottom: 15px;
}

/* =========================
BADGES
========================= */

.badge {
    display:inline-block;
    padding:6px 12px;
    border-radius:20px;
    font-size:12px;
    font-weight:bold;
    margin-right:8px;
}

.badge-green {
    background:#dcfce7;
    color:#166534;
}

.badge-red {
    background:#fee2e2;
    color:#991b1b;
}

.badge-blue {
    background:#dbeafe;
    color:#1d4ed8;
}

.kpi-title {
    font-size:16px;
    color:#6b7280;
}

.kpi-value {
    font-size:34px;
    font-weight:bold;
    color:#2563eb;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# CONEXION
# =========================================================

def get_conn_logistica():

    conn = sqlite3.connect(
        get_db_path("logistica")
    )

    conn.row_factory = sqlite3.Row

    return conn


# =========================================================
# APP
# =========================================================

def consulta_clientes_logistica_app():

    conn = get_conn_logistica()

    try:

        # =====================================================
        # TITULO
        # =====================================================

        html_card("""
        <div class='main-title'>
            🚚 Consulta Clientes - Logística
        </div>

        <div class='sub-title'>
            Dashboard ejecutivo clientes logísticos
        </div>
        """)

        # =====================================================
        # FILTROS
        # =====================================================

        with st.container(border=True):

            f1, f2, f3, f4, f5 = st.columns(5)

            with f1:
                filtro_cliente = st.text_input(
                    "🔎 Cliente"
                )

            with f2:
                filtro_ciudad = st.text_input(
                    "🏙️ Ciudad"
                )

            with f3:
                filtro_estado = st.text_input(
                    "📍 Estado"
                )

            with f4:
                filtro_ruta = st.text_input(
                    "🚚 Ruta"
                )

            with f5:
                filtro_estatus = st.selectbox(
                    "📊 Estatus",
                    ["Todos", "Activo", "Inactivo"]
                )

        # =====================================================
        # QUERY
        # =====================================================

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

            params.extend([
                valor,
                valor,
                valor
            ])

        if filtro_ciudad:

            query += """
            AND ciudad LIKE ?
            """

            params.append(
                f"%{filtro_ciudad}%"
            )

        if filtro_estado:

            query += """
            AND estado LIKE ?
            """

            params.append(
                f"%{filtro_estado}%"
            )

        if filtro_ruta:

            query += """
            AND ruta LIKE ?
            """

            params.append(
                f"%{filtro_ruta}%"
            )

        if filtro_estatus != "Todos":

            query += """
            AND estatus = ?
            """

            params.append(
                filtro_estatus
            )

        query += """
        ORDER BY nombre_cliente
        """

        df = pd.read_sql_query(
            query,
            conn,
            params=params
        )

        if df.empty:

            st.warning(
                "No se encontraron clientes."
            )

            return

        # =====================================================
        # KPIS
        # =====================================================

        k1, k2, k3, k4 = st.columns(4)

        with k1:

            html_card(f"""
            <div class='card'>
                <div class='kpi-title'>👥 Clientes</div>
                <div class='kpi-value'>{len(df)}</div>
            </div>
            """)

        with k2:

            total_criticos = len(
                df[
                    df["cliente_critico"]
                    .astype(str)
                    .str.lower()
                    .isin(["si","sí","1","true"])
                ]
            )

            html_card(f"""
            <div class='card'>
                <div class='kpi-title'>🚨 Críticos</div>
                <div class='kpi-value'>{total_criticos}</div>
            </div>
            """)

        with k3:

            total_cita = len(
                df[
                    df["requiere_cita"]
                    .astype(str)
                    .str.lower()
                    .isin(["si","sí","1","true"])
                ]
            )

            html_card(f"""
            <div class='card'>
                <div class='kpi-title'>📅 Requiere cita</div>
                <div class='kpi-value'>{total_cita}</div>
            </div>
            """)

        with k4:

            total_gps = len(
                df[
                    df["gps_obligatorio"]
                    .astype(str)
                    .str.lower()
                    .isin(["si","sí","1","true"])
                ]
            )

            html_card(f"""
            <div class='card'>
                <div class='kpi-title'>📡 GPS obligatorio</div>
                <div class='kpi-value'>{total_gps}</div>
            </div>
            """)

        # =====================================================
        # CLIENTE
        # =====================================================

        cliente_select = st.selectbox(
            "🧾 Cliente ejecutivo",
            df["nombre_cliente"]
            .dropna()
            .unique()
        )

        cliente = df[
            df["nombre_cliente"]
            == cliente_select
        ].iloc[0]

        st.write("")

        # =====================================================
        # CARDS PRINCIPALES
        # =====================================================

        c1, c2, c3 = st.columns([2,2,1])

        # =====================================================
        # PERFIL CLIENTE
        # =====================================================

        with c1:

            html_card(f"""
            <div class='card'>

                <div style='font-size:22px;
                            font-weight:bold;
                            margin-bottom:15px;'>

                    🧾 PERFIL CLIENTE

                </div>

                <div style='margin-bottom:15px;'>

                    <span class='badge badge-green'>
                        {cliente['estatus']}
                    </span>

                    <span class='badge badge-red'>
                        Cliente crítico
                    </span>

                    <span class='badge badge-blue'>
                        GPS obligatorio
                    </span>

                </div>

                <div style='line-height:2;'>

                    <b>Código:</b>
                    {cliente['codigo_cliente']}<br>

                    <b>Cliente:</b>
                    {cliente['nombre_cliente']}<br>

                    <b>Razón social:</b>
                    {cliente['razon_social']}<br>

                    <b>RFC:</b>
                    {cliente['rfc']}<br>

                    <b>Ciudad:</b>
                    {cliente['ciudad']}<br>

                    <b>Estado:</b>
                    {cliente['estado']}

                </div>

            </div>
            """)

        # =====================================================
        # OPERACION
        # =====================================================

        with c2:

            html_card(f"""
            <div class='card'>

                <div style='font-size:22px;
                            font-weight:bold;
                            margin-bottom:15px;'>

                    🚚 OPERACIÓN LOGÍSTICA

                </div>

                <div style='line-height:2;'>

                    <b>Ruta:</b>
                    {cliente['ruta']}<br>

                    <b>Horario recepción:</b>
                    {cliente['hora_inicio_recepcion']}
                    -
                    {cliente['hora_fin_recepcion']}<br>

                    <b>Días entrega:</b>
                    {cliente['dias_entrega_permitidos']}<br>

                    <b>Tiempo descarga:</b>
                    {cliente['tiempo_descarga_min']}<br>

                    <b>Nivel servicio:</b>
                    {cliente['nivel_servicio']}

                </div>

            </div>
            """)

        # =====================================================
        # RESTRICCIONES
        # =====================================================

        with c3:

            html_card(f"""
            <div class='card'>

                <div style='font-size:22px;
                            font-weight:bold;
                            margin-bottom:15px;'>

                    ⚠️ RESTRICCIONES

                </div>

                <div style='line-height:2;'>

                    <b>Requiere cita:</b>
                    {cliente['requiere_cita']}<br>

                    <b>GPS:</b>
                    {cliente['gps_obligatorio']}<br>

                    <b>Unidad:</b>
                    {cliente['tipo_unidad_permitida']}<br>

                    <b>Entrega parcial:</b>
                    {cliente['permite_entrega_parcial']}<br>

                    <b>Tarima:</b>
                    {cliente['tipo_tarima']}

                </div>

            </div>
            """)

        # =====================================================
        # MAPA
        # =====================================================

        st.write("")

        mapa_col1, mapa_col2 = st.columns([2,1])

        with mapa_col1:

            with st.container(border=True):

                st.subheader(
                    "🗺️ Ubicación geográfica"
                )

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

                    st.info(
                        "Cliente sin coordenadas."
                    )

        with mapa_col2:

            html_card(f"""
            <div class='card'>

                <div style='font-size:22px;
                            font-weight:bold;
                            margin-bottom:15px;'>

                    📞 CONTACTO

                </div>

                <div style='line-height:2;'>

                    <b>Contacto:</b>
                    {cliente['contacto_entrega']}<br>

                    <b>Teléfono:</b>
                    {cliente['telefono_contacto']}<br>

                    <b>Correo:</b>
                    {cliente['correo_contacto']}<br>

                    <b>Dirección:</b>
                    {cliente['direccion_entrega']}

                </div>

            </div>
            """)

        # =====================================================
        # TABS
        # =====================================================

        tab1, tab2, tab3 = st.tabs([
            "📦 Entrega",
            "🚚 Restricciones",
            "📋 Grid clientes"
        ])

        with tab1:

            e1, e2, e3, e4 = st.columns(4)

            with e1:
                st.metric(
                    "📦 Emplaye",
                    cliente["requiere_emplaye"]
                )

            with e2:
                st.metric(
                    "🏷️ Etiqueta",
                    cliente["requiere_etiqueta"]
                )

            with e3:
                st.metric(
                    "📄 Factura",
                    cliente["requiere_factura_impresa"]
                )

            with e4:
                st.metric(
                    "📷 Foto",
                    cliente["requiere_foto_entrega"]
                )

        with tab2:

            r1, r2, r3 = st.columns(3)

            with r1:
                st.metric(
                    "⚖️ Peso máx",
                    cliente["peso_max_tarima"]
                )

            with r2:
                st.metric(
                    "📏 Altura máx",
                    cliente["altura_max_tarima"]
                )

            with r3:
                st.metric(
                    "🚚 Unidad",
                    cliente["tipo_unidad_permitida"]
                )

        with tab3:

            columnas = [
                "codigo_cliente",
                "nombre_cliente",
                "ciudad",
                "estado",
                "ruta",
                "estatus",
                "requiere_cita",
                "gps_obligatorio",
                "cliente_critico",
                "nivel_servicio"
            ]

            st.dataframe(
                df[columnas],
                use_container_width=True,
                height=450
            )

            csv = df.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                "📥 Descargar CSV",
                csv,
                "clientes_logistica.csv",
                "text/csv"
            )

    except Exception as e:

        st.error(
            f"Error: {e}"
        )

    finally:

        conn.close()
