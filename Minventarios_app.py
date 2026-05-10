import streamlit as st

from menu_dinamico import sidebar_dinamico
from compras_app import compras_app
from logistica_app import logistica_app
from wms_app import wms_app
from mantenimiento_app import mantenimiento_app


st.set_page_config(
    page_title="SIGEM",
    layout="wide"
)

# =========================
# LOGIN TEMPORAL DESACTIVADO
# =========================

st.session_state.autenticado = True
st.session_state.usuario = "admin"
st.session_state.nombre = "Administrador"
st.session_state.rol = "Administrador"


# =========================
# NUEVO SIGEM PRINCIPAL
# =========================

ruta = "Minventarios"

if ruta == "Minventarios":

    st.title("📦 Módulo de Inventarios")

    from sidebar_inventarios import sidebar_inventarios

    opcion_inv = sidebar_inventarios()
    # =========================
# SUBMENUS INVENTARIOS
# =========================

if opcion_inv == "Productos":

    st.subheader("📦 Productos")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.info("📋 Catálogo de productos")

    with c2:
        st.success("🏷️ Clasificaciones")

    with c3:
        st.warning("📍 Ubicaciones")

elif opcion_inv == "Entradas":

    st.subheader("📥 Entradas")

    st.text_input("Documento")
    st.date_input("Fecha")
    st.selectbox("Tipo entrada", [
        "Compra",
        "Producción",
        "Transferencia"
    ])

    st.button("💾 Guardar entrada")

elif opcion_inv == "Salidas":

    st.subheader("📤 Salidas")

    st.text_input("Documento salida")
    st.selectbox("Motivo", [
        "Venta",
        "Consumo",
        "Merma"
    ])

    st.button("💾 Guardar salida")

elif opcion_inv == "Transferencias":

    st.subheader("🔁 Transferencias")

    c1, c2 = st.columns(2)

    with c1:
        st.selectbox("Origen", [
            "CEDI",
            "Almacén Norte"
        ])

    with c2:
        st.selectbox("Destino", [
            "Sucursal",
            "Producción"
        ])

    st.button("🚚 Transferir")

elif opcion_inv == "Kardex":

    st.subheader("📋 Kardex")

    st.dataframe({
        "Producto": ["A", "B"],
        "Entrada": [100, 50],
        "Salida": [20, 10],
        "Saldo": [80, 40]
    })

elif opcion_inv == "Existencias":

    st.subheader("🔍 Existencias")

    st.metric("Total SKUs", 1250)
    st.metric("Inventario valorizado", "$2,450,000")

elif opcion_inv == "Conteos cíclicos":

    st.subheader("📌 Conteos cíclicos")

    st.checkbox("Iniciar conteo")
    st.button("✅ Confirmar")

elif opcion_inv == "Ajustes":

    st.subheader("✅ Ajustes de inventario")

    st.text_area("Motivo ajuste")
    st.button("💾 Aplicar ajuste")

    st.write("Opción seleccionada:", opcion_inv)

          
elif ruta == "compras":
    st.title("🛒 Compras")
    compras_app()

elif ruta == "logistica":
    st.title("🚚 Logística")
    logistica_app()

elif ruta == "wms":
    st.title("🏬 WMS")
    wms_app()

elif ruta == "mantenimiento":
    st.title("🛠️ Mantenimiento")
    mantenimiento_app()

else:
    st.warning(f"Ruta no configurada: {ruta}")
