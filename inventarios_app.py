import streamlit as st
import pandas as pd


# =========================
# 1. UPLOADERS (PRIMERO)
# =========================
st.markdown("### 📂 Carga de archivos")

archivo_prod = st.file_uploader("📦 Productos", type=["xlsx"], key="prod_file")
archivo_mov = st.file_uploader("📊 Movimientos", type=["xlsx"], key="mov_file")
archivo_inv = st.file_uploader("🏭 Inventario", type=["xlsx"], key="inv_file")

# =========================
# 2. GUARDAR
# =========================
if archivo_prod:
    df_prod = pd.read_excel(archivo_prod)
    df_prod.columns = df_prod.columns.str.strip()
    st.session_state.productos = df_prod

if archivo_mov:
    df_mov = pd.read_excel(archivo_mov)
    df_mov.columns = df_mov.columns.str.strip()
    st.session_state.movimientos = df_mov

if archivo_inv:
    df_inv = pd.read_excel(archivo_inv)
    df_inv.columns = df_inv.columns.str.strip()
    st.session_state.inventario = df_inv

# =========================
# 3. VALIDAR (DESPUÉS)
# =========================
productos = st.session_state.get("productos")
movimientos = st.session_state.get("movimientos")
inventario = st.session_state.get("inventario")

if not (productos_file and movimientos_file and inventario_file):
        st.warning("⚠️ Debes cargar los 3 archivos")
        return   # 👈 MUY IMPORTANT
if productos is None or movimientos is None or inventario is None:
        st.warning("⚠️ Debes cargar los 3 archivos")
        return    

if archivo_prod:
    df_prod = pd.read_excel(archivo_prod)
    df_prod.columns = df_prod.columns.str.strip()
    st.session_state.productos = df_prod

if archivo_mov:
    df_mov = pd.read_excel(archivo_mov)
    df_mov.columns = df_mov.columns.str.strip()
    st.session_state.movimientos = df_mov

if archivo_inv:
    df_inv = pd.read_excel(archivo_inv)
    df_inv.columns = df_inv.columns.str.strip()
    st.session_state.inventario = df_inv

productos = st.session_state.get("productos")
movimientos = st.session_state.get("movimientos")
inventario = st.session_state.get("inventario")

    
    # =========================
    # ESTADO
    # =========================
if "inv_vista" not in st.session_state:
    st.session_state.inv_vista = "menu"
    st.write("Vista:", st.session_state.inv_vista)
    

    # =========================
    # CALCULO KPI RAPIDO
    # =========================
    movimientos["TIPO"] = movimientos["TIPO"].str.upper().str.strip()

    movimientos["ENTRADA"] = movimientos["CANTIDAD"].where(movimientos["TIPO"]=="COMPRA", 0)
    movimientos["SALIDA"] = movimientos["CANTIDAD"].where(movimientos["TIPO"]=="VENTA", 0)

    stock = movimientos.groupby("ID_PRODUCTO")[["ENTRADA","SALIDA"]].sum().reset_index()
    stock["STOCK"] = stock["ENTRADA"] - stock["SALIDA"]

    df = stock.merge(productos, on="ID_PRODUCTO", how="left")
    df = df.merge(inventario, on="ID_PRODUCTO", how="left")

    # KPI
    total_stock = int(df["STOCK"].sum())
    criticos = df[df["STOCK"] < df["STOCK_MIN"]].shape[0]
    sobrestock = df[df["STOCK"] > df["STOCK_MAX"]].shape[0]
    rotacion = (df["SALIDA"].sum() / df["STOCK"].sum()) if df["STOCK"].sum() != 0 else 0

    # =========================
    # MENU CARDS
    # =========================
    if st.session_state.inv_vista == "menu":

        st.markdown("## 📦 Panel de Inventarios")

        # CSS PRO
        st.markdown("""
        <style>
        .card {
            padding:20px;
            border-radius:15px;
            background:#f8fafc;
            box-shadow:0 4px 10px rgba(0,0,0,0.05);
            text-align:center;
        }
        </style>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        c4, c5, _ = st.columns(3)

        # -------- CARD 1 --------
        with c1:
            st.markdown(f"""
            <div class="card">
                <h4>📊 Dashboard</h4>
                <h2>{total_stock:,}</h2>
                <p>Stock Total</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Ver", key="c1"):
                st.session_state.inv_vista = "dash1"
                st.rerun()

        # -------- CARD 2 --------
        with c2:
            st.markdown(f"""
            <div class="card">
                <h4>🚨 Críticos</h4>
                <h2 style="color:red;">{criticos}</h2>
                <p>Productos bajo mínimo</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Ver", key="c2"):
                st.session_state.inv_vista = "dash2"
                st.rerun()

        # -------- CARD 3 --------
        with c3:
            st.markdown(f"""
            <div class="card">
                <h4>⚠️ Sobrestock</h4>
                <h2 style="color:orange;">{sobrestock}</h2>
                <p>Exceso inventario</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Ver", key="c3"):
                st.session_state.inv_vista = "dash3"
                st.rerun()

        # -------- CARD 4 --------
        with c4:
            st.markdown(f"""
            <div class="card">
                <h4>📈 Rotación</h4>
                <h2>{rotacion:.2f}</h2>
                <p>Movimiento</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Ver", key="c4"):
                st.session_state.inv_vista = "dash4"
                st.rerun()

        # -------- CARD 5 --------
        with c5:
            st.markdown(f"""
            <div class="card">
                <h4>🧠 Recomendaciones</h4>
                <h2>AI</h2>
                <p>Decisiones</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Ver", key="c5"):
                st.session_state.inv_vista = "dash5"
                st.rerun()

    # =========================
    # DASHBOARDS
    # =========================
    else:

        if st.button("⬅️ Volver"):
            st.session_state.inv_vista = "menu"
            st.rerun()

        if st.session_state.inv_vista == "dash1":
            st.markdown("## 📊 Dashboard General")

        elif st.session_state.inv_vista == "dash2":
            st.markdown("## 🚨 Productos Críticos")

        elif st.session_state.inv_vista == "dash3":
            st.markdown("## ⚠️ Sobrestock")

        elif st.session_state.inv_vista == "dash4":
            st.markdown("## 📈 Rotación")

        elif st.session_state.inv_vista == "dash5":
            st.markdown("## 🧠 Recomendaciones")

