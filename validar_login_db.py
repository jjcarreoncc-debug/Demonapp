
import sqlite3
import hashlib
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

DB_PATH = BASE_DIR / "erp.db"


# =====================================
# HASH PASSWORD
# =====================================
def hash_password(password):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()


# =====================================
# VALIDAR LOGIN
# =====================================
def validar_login_db(usuario, password):

    conn = sqlite3.connect(DB_PATH)

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    try:

        row = cursor.execute(
            """
            SELECT
                usuario,
                nombre,
                password_hash,
                estado,
                id_rol
            FROM usuarios
            WHERE TRIM(UPPER(usuario))
                  =
                  TRIM(UPPER(?))
            """,
            (usuario,)
        ).fetchone()

    except Exception as e:

        conn.close()

        return {
            "ok": False,
            "mensaje": f"Error SQL: {e}",
            "data": None
        }

    conn.close()

    if row is None:

        return {
            "ok": False,
            "mensaje": "Usuario no encontrado",
            "data": None
        }

    password_bd = str(
        row["password_hash"]
    ).strip()

    password_ingresado = str(
        password
    ).strip()

    password_hash = hash_password(
        password_ingresado
    )

    if (
        password_bd != password_ingresado
        and password_bd != password_hash
    ):

        return {
            "ok": False,
            "mensaje": "Password incorrecto",
            "data": None
        }

    return {
        "ok": True,
        "mensaje": "Login correcto",
        "data": {
            "usuario": row["usuario"],
            "nombre": row["nombre"],
            "id_rol": row["id_rol"]
        }
    }
