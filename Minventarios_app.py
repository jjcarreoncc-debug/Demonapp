# =========================
# IMPORTS APPS
# =========================
from alta_material_app import alta_material_app
from baja_material_app import baja_material_app
from consulta_material_app import consulta_material_app

#from alta_sku_app import alta_sku_app
#from baja_sku_app import baja_sku_app
#from consulta_sku_app import consulta_sku_app


# =========================
# MAIN
# =========================
menu_inv, submenu_inv, opcion_inv = sidebar_inventarios()

st.caption(f"{menu_inv} / {submenu_inv} / {opcion_inv}")


# =========================
# ROUTER
# =========================
if opcion_inv == "Alta de material":
    alta_material_app()

elif opcion_inv == "Baja de material":
    baja_material_app()

elif opcion_inv == "Consulta de material":
    consulta_material_app()

elif opcion_inv == "Alta de SKU":
    alta_sku_app()

elif opcion_inv == "Baja de SKU":
    baja_sku_app()

elif opcion_inv == "Consulta de SKU":
    consulta_sku_app()

else:
    pantalla_placeholder(opcion_inv)
