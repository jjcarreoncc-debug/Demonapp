from database import get_connection


# =====================================
# OBTENER MENU USUARIO
# =====================================
def obtener_menu_usuario(rol):

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT
            m.nombre_modulo
        FROM permisos_roles pr

        INNER JOIN roles r
            ON pr.id_rol = r.id_rol

        INNER JOIN modulos m
            ON pr.id_modulo = m.id_modulo

        WHERE
            r.nombre_rol = ?
            AND pr.puede_ver = 1
            AND m.activo = 1

        ORDER BY
            m.orden_menu
    """

    cursor.execute(
        query,
        (rol,)
    )

    resultados = cursor.fetchall()

    conn.close()

    menu = ["Inicio"]

    for row in resultados:

        menu.append(
            row["nombre_modulo"]
        )

    return menu


# =====================================
# VALIDAR ACCESO
# =====================================
def tiene_acceso(
    rol,
    modulo
):

    menu_usuario = obtener_menu_usuario(rol)

    return modulo in menu_usuario
