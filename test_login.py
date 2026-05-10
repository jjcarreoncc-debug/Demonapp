from database import get_connection


def mostrar_tabla(conn, tabla):

    print(f"\n===== {tabla} =====")

    try:

        cur = conn.cursor()

        cur.execute(f"SELECT * FROM {tabla}")

        filas = cur.fetchall()

        for fila in filas:
            print(dict(fila))

        if not filas:
            print("(vacía)")

    except Exception as e:

        print(f"Error leyendo {tabla}: {e}")


def main():

    conn = get_connection()

    cur = conn.cursor()

    print("\n==============================")
    print("ESTADO ACTUAL DE LA BASE")
    print("==============================")

    mostrar_tabla(conn, "roles")
    mostrar_tabla(conn, "modulos")
    mostrar_tabla(conn, "permisos_roles")

    print("\n==============================")
    print("CREANDO ADMINISTRADOR")
    print("==============================")

    # =========================
    # CREAR ROL ADMINISTRADOR
    # =========================

    cur.execute("""
        INSERT OR IGNORE INTO roles (
            nombre_rol
        )
        VALUES (
            'Administrador'
        )
    """)

    conn.commit()

    # =========================
    # CREAR MODULO MANTENIMIENTO
    # =========================

    try:

        cur.execute("""
            INSERT OR IGNORE INTO modulos (
                nombre_modulo,
                icono,
                ruta,
                orden_menu,
                activo
            )
            VALUES (
                'Mantenimiento',
                '🛠️',
                'mantenimiento',
                1,
                1
            )
        """)

        conn.commit()

    except Exception as e:

        print("\n❌ ERROR INSERTANDO MODULO:")
        print(e)

    # =========================
    # VALIDAR MODULO
    # =========================

    cur.execute("""
        SELECT *
        FROM modulos
    """)

    print("\n===== MODULOS DESPUES INSERT =====")

    for fila in cur.fetchall():
        print(dict(fila))

    # =========================
    # OBTENER ID ROL
    # =========================

    cur.execute("""
        SELECT id_rol
        FROM roles
        WHERE nombre_rol = 'Administrador'
    """)

    fila_rol = cur.fetchone()

    if fila_rol is None:

        print("❌ No existe el rol Administrador")

        conn.close()

        return

    id_rol = fila_rol[0]

    # =========================
    # OBTENER ID MODULO
    # =========================

    cur.execute("""
        SELECT id_modulo
        FROM modulos
        WHERE ruta = 'mantenimiento'
    """)

    fila_modulo = cur.fetchone()

    if fila_modulo is None:

        print("❌ No se encontró el módulo mantenimiento")
        print("⚠️ Revisa columnas obligatorias en modulos")

        conn.close()

        return

    id_modulo = fila_modulo[0]

    # =========================
    # DAR PERMISOS
    # =========================

    cur.execute("""
        INSERT OR IGNORE INTO permisos_roles (
            id_rol,
            id_modulo,
            puede_ver
        )
        VALUES (?, ?, 1)
    """, (id_rol, id_modulo))

    conn.commit()

    print("\n==============================")
    print("ESTADO FINAL")
    print("==============================")

    mostrar_tabla(conn, "roles")
    mostrar_tabla(conn, "modulos")
    mostrar_tabla(conn, "permisos_roles")

    conn.close()

    print("\n✅ Setup terminado correctamente")


if __name__ == "__main__":

    main()
