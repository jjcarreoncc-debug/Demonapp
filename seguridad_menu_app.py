import sqlite3

from sigem_db import get_db_path


# =====================================
# CONEXION SEGURIDAD
# =====================================
def get_conn_seguridad():

    db_path = get_db_path("seguridad")

    conn = sqlite3.connect(db_path)

    conn.row_factory = sqlite3.Row

    return conn


# =====================================
# NORMALIZAR ROL
# =====================================
def normalizar_rol(rol):

    if rol is None:

        return ""

    return str(rol).strip()


# =====================================
# OBTENER MENU USUARIO
# =====================================
def obtener_menu_usuario(rol):

    rol = normalizar_rol(rol)

    if not rol:

        return ["Inicio"]

    conn = get_conn_seguridad()

    cursor = conn.cursor()

    query = """
        SELECT DISTINCT
            m.nombre_modulo
        FROM permisos_roles pr

        INNER JOIN roles r
            ON pr.id_rol = r.id_rol

        INNER JOIN modulos m
            ON pr.id_modulo = m.id_modulo

        WHERE
            TRIM(r.nombre_rol) = TRIM(?)
            AND pr.puede_ver = 1
            AND IFNULL(m.activo, 1) = 1

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

    rol = normalizar_rol(rol)

    modulo = str(modulo).strip()

    menu_usuario = obtener_menu_usuario(rol)

    return modulo in menu_usuario
