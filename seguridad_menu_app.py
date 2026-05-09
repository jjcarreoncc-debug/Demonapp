# =====================================
# MENU SEGUN ROL
# =====================================

def obtener_menu_usuario(rol):

    if rol == "Admin":

        return [
            "Inicio",
            "Dashboard",
            "Inventarios",
            "Compras",
            "logistica",
            "Almacen WMS",
            "Mantenimiento"
        ]

    elif rol == "Compras":

        return [
            "Inicio",
            "Compras"
        ]

    elif rol == "Logistica":

        return [
            "Inicio",
            "logistica"
        ]

    elif rol == "WMS":

        return [
            "Inicio",
            "Almacen WMS"
        ]

    elif rol == "Gerencia":

        return [
            "Inicio",
            "Dashboard",
            "Inventarios",
            "Compras",
            "logistica"
        ]

    else:

        return [
            "Inicio"
        ]


# =====================================
# VALIDAR ACCESO
# =====================================

def tiene_acceso(
    rol,
    modulo
):

    menu_usuario = obtener_menu_usuario(rol)

    return modulo in menu_usuario
