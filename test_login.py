from database import get_connection


def mostrar_estructura(cur, tabla):

    print(f"\n===== ESTRUCTURA {tabla} =====")

    cur.execute(f"PRAGMA table_info({tabla})")

    columnas = cur.fetchall()

    for col in columnas:
        print(col)


def mostrar_datos(cur, tabla):

    print(f"\n===== DATOS {tabla} =====")

    try:

        cur.execute(f"SELECT * FROM {tabla}")

        filas = cur.fetchall()

        for fila in filas:
            print(fila)

        if not filas:
            print("(vacía)")

    except Exception as e:

        print(e)


def main():

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

    print("\n✅ Diagnóstico terminado")


if __name__ == "__main__":

    main()
