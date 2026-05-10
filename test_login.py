from database import get_connection


def mostrar_estructura(cur, tabla):

    print("\n==============================")
    print(f"ESTRUCTURA TABLA: {tabla}")
    print("==============================")

    try:

        cur.execute(f"PRAGMA table_info({tabla})")

        columnas = cur.fetchall()

        for col in columnas:
            print(col)

        if not columnas:
            print("(sin columnas)")

    except Exception as e:

        print(f"ERROR: {e}")


def mostrar_datos(cur, tabla):

    print("\n==============================")
    print(f"DATOS TABLA: {tabla}")
    print("==============================")

    try:

        cur.execute(f"SELECT * FROM {tabla}")

        filas = cur.fetchall()

        for fila in filas:
            print(fila)

        if not filas:
            print("(vacía)")

    except Exception as e:

        print(f"ERROR: {e}")


def main():

    print("\n===================================")
    print("DIAGNOSTICO BASE DE DATOS SIGEM")
    print("===================================")

    conn = get_connection()

    cur = conn.cursor()

    tablas = [
        "roles",
        "modulos",
        "permisos_roles",
        "usuarios"
    ]

    for tabla in tablas:

        mostrar_estructura(cur, tabla)

        mostrar_datos(cur, tabla)

    conn.close()

    print("\n===================================")
    print("DIAGNOSTICO TERMINADO")
    print("===================================")


if __name__ == "__main__":

    main()
