import streamlit as st
import pandas as pd
import sqlite3
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
# CSS
# =========================================================

st.markdown("""
<style>

/* ===== GENERAL ===== */

.main {
    background-color: #f5f7fb;
}

.block-container {
    padding-top: 1rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

/* ===== KPI ===== */

.kpi-card {
    background: white;
    padding: 18px;
    border-radius: 18px;
    box-shadow: 0px 2px 10px rgba(0,0,0,0.08);
    border-left: 6px solid #2563eb;
}

.kpi-title {
    font-size: 15px;
    color: gray;
}

.kpi-value {
    font-size: 34px;
    font-weight: bold;
    color: #111827;
}

/* ===== CARDS ===== */

.card {
    background: white;
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0px 2px 12px rgba(0,0,0,0.08);
    margin-bottom: 15px;
}

.card-title {
    font-size: 24px;
    font-weight: bold;
    color: #111827;
}

.card-subtitle {
    color: gray;
    margin-bottom: 15px;
}

/* ===== BADGES ===== */

.badge {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 20px;
    margin-right: 8px;
    font-size: 12px;
    font-weight: bold;
}

.badge-green {
    background: #dcfce7;
    color: #166534;
}

.badge-blue {
    background: #dbeafe;
    color: #1d4ed8;
}

.badge-red {
    background: #fee2e2;
    color: #991b1b;
}

/* ===== GRID ===== */

.grid-card {
    background: white;
    padding: 15px;
    border-radius: 18px;
    box-shadow: 0px 2px 12px rgba(0,0,0,0.08);
}

/* ===== TABS ===== */

.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
}

.stTabs [data-baseweb="tab"] {
    background-color: white;
    border-radius: 12px;
    padding: 10px 20px;
}

/* ===== METRIC ===== */

[data-testid="metric-container"] {
    background: white;
    border-radius: 18px;
    padding: 15px;
    box-shadow: 0px 2px 12px rgba(0,0,0,0.08);
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

    st.title(
        "🚚 Consulta Clientes - Logística"
    )

    conn = get_conn_logistica()

    # =========================================================
    # FILTROS
    # =========================================================

    with st.container(border=True):

        f1, f2, f3, f4, f5 = st.columns(5)

        with f1:
            filtro_cliente = st.text_input(
                "Buscar cliente"
            )

        with f2:
            filtro_ciudad = st.text_input(
                "Ciudad"
            )

        with f3:
            filtro_estado = st.text_input(
                "Estado"
            )

        with f4:
            filtro_ruta = st.text_input(
                "Ruta"
            )

        with f5:
            filtro_estatus = st.selectbox(
                "Estatus",
                ["Todos", "Activo", "Inactivo"]
            )

    # =========================================================
    # QUERY
    # =========================================================

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

    try:

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

        # =========================================================
        # KPIS
        # =========================================================

        k1, k2, k3, k4, k5 = st.columns(5)

        with k1:
            st.metric(
                "👥 Clientes",
                len(df)
            )

        with k2:
            st.metric(
                "🚨 Críticos",
                len(
                    df[
                        df["cliente_critico"]
                        .astype(str)
                        .str.lower()
                        .isin(["si", "sí", "1", "true"])
                    ]
                )
            )

        with k3:
            st.metric(
                "📅 Requiere cita",
                len(
                    df[
                        df["requiere_cita"]
                        .astype(str)
                        .str.lower()
                        .isin(["si", "sí", "1", "true"])
                    ]
                )
            )

        with k4:
            st.metric(
                "📡 GPS",
                len(
                    df[
                        df["gps_obligatorio"]
                        .astype(str)
                        .str.lower()
                        .isin(["si", "sí", "1", "true"])
                    ]
                )
            )

        with k5:
            st.metric(
                "🚚 Rutas",
                df["ruta"].nunique()
            )

        st.divider()

        # =========================================================
        # CLIENTE
        # =========================================================

        cliente_select = st.selectbox(
            "Selecciona cliente",
            df["nombre_cliente"]
            .dropna()
            .unique()
        )

        cliente = df[
            df["nombre_cliente"]
            == cliente_select
        ].iloc[0]

        left, right = st.columns([2, 1])

        # =========================================================
        # PERFIL CLIENTE
        # =========================================================

        with left:

            st.markdown(f"""
            <div class="card">

                <div class="card-title">
                    {cliente['nombre_cliente']}
                </div>

                <div class="card-subtitle">
                    {cliente['razon_social']}
                </div>

                <span class="badge badge-green">
                    {cliente['estatus']}
                </span>

                <span class="badge badge-red">
                    Cliente Crítico
                </span>

                <span class="badge badge-blue">
                    GPS Obligatorio
                </span>

                <hr>

                <b>📍 Ciudad:</b>
                {cliente['ciudad']}, {cliente['estado']}

                <br><br>

                <b>🚚 Ruta:</b>
                {cliente['ruta']}

                <br><br>

                <b>📅 Horario recepción:</b>
                {cliente['hora_inicio_recepcion']}
                -
                {cliente['hora_fin_recepcion']}

                <br><br>

                <b>📞 Contacto:</b>
                {cliente['contacto_entrega']}

                <br><br>

                <b>☎️ Teléfono:</b>
                {cliente['telefono_contacto']}

                <br><br>

                <b>📧 Correo:</b>
                {cliente['correo_contacto']}

                <br><br>

                <b>📝 Observaciones:</b>
                {cliente['observaciones_logisticas']}

            </div>
            """, unsafe_allow_html=True)

        # =========================================================
        # MAPA / KPIS
        # =========================================================

        with right:

            st.markdown("""
            <div class="card">

                <div class="card-title">
                    📊 Indicadores
                </div>

                <hr>

                <b>🚚 Nivel servicio:</b>
                Premium

                <br><br>

                <b>📦 Tipo tarima:</b>
                CHEP

                <br><br>

                <b>📡 GPS:</b>
                Obligatorio

                <br><br>

                <b>🚨 Restricción unidad:</b>
                Rabón

                <br><br>

                <b>📅 Requiere cita:</b>
                Sí

            </div>
            """, unsafe_allow_html=True)

        # =========================================================
        # TABS
        # =========================================================

        tab1, tab2, tab3, tab4 = st.tabs([
            "📞 Contacto",
            "🚚 Restricciones",
            "📦 Operación",
            "📋 Grid"
        ])

        # =========================================================
        # CONTACTO
        # =========================================================

        with tab1:

            c1, c2 = st.columns(2)

            with c1:

                st.markdown(f"""
                <div class="card">

                <h4>📞 Información contacto</h4>

                <b>Contacto:</b>
                {cliente['contacto_entrega']}

                <br><br>

                <b>Teléfono:</b>
                {cliente['telefono_contacto']}

                <br><br>

                <b>Correo:</b>
                {cliente['correo_contacto']}

                </div>
                """, unsafe_allow_html=True)

            with c2:

                st.markdown(f"""
                <div class="card">

                <h4>📍 Dirección</h4>

                <b>Dirección:</b>
                {cliente['direccion_entrega']}

                <br><br>

                <b>Colonia:</b>
                {cliente['colonia']}

                <br><br>

                <b>Código postal:</b>
                {cliente['codigo_postal']}

                </div>
                """, unsafe_allow_html=True)

        # =========================================================
        # RESTRICCIONES
        # =========================================================

        with tab2:

            r1, r2, r3 = st.columns(3)

            with r1:
                st.metric(
                    "📅 Requiere cita",
                    cliente['requiere_cita']
                )

            with r2:
                st.metric(
                    "📡 GPS",
                    cliente['gps_obligatorio']
                )

            with r3:
                st.metric(
                    "🚚 Unidad",
                    cliente['tipo_unidad_permitida']
                )

        # =========================================================
        # OPERACION
        # =========================================================

        with tab3:

            o1, o2, o3 = st.columns(3)

            with o1:

                st.metric(
                    "⏱️ Descarga",
                    cliente['tiempo_descarga_min']
                )

            with o2:

                st.metric(
                    "📦 Peso Máx",
                    cliente['peso_max_tarima']
                )

            with o3:

                st.metric(
                    "📏 Altura Máx",
                    cliente['altura_max_tarima']
                )

        # =========================================================
        # GRID
        # =========================================================

        with tab4:

            st.dataframe(
                df,
                use_container_width=True,
                height=400
            )

            csv = df.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                label="📥 Exportar CSV",
                data=csv,
                file_name="clientes_logistica.csv",
                mime="text/csv"
            )

    except Exception as e:

        st.error(
            f"Error: {e}"
        )

    finally:

        conn.close()
