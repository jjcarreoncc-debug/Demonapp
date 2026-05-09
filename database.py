
import sqlite3

from pathlib import Path


# =====================================
# RUTA BASE
# =====================================
BASE_DIR = Path(__file__).resolve().parent

DB_PATH = BASE_DIR / "erp.db"


# =====================================
# CONEXION
# =====================================
def get_connection():

    conn = sqlite3.connect(
        DB_PATH,
        check_same_thread=False
    )

    conn.row_factory = sqlite3.Row

    return conn
# =====================================
# INIT DATABASE
# =====================================
def init_database():

    conn = get_connection()

    conn.close()
