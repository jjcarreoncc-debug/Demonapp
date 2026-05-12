import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


DB_CONFIG = {
    "erp": BASE_DIR / "erp.db",

    "materiales": BASE_DIR / "materiales.db",

    "compras": BASE_DIR / "compras.db",

    "inventarios": BASE_DIR / "inventarios.db",

    "logistica": BASE_DIR / "logistica.db",

    "wms": BASE_DIR / "wms.db",
}


def get_db_path(nombre_db):

    path = DB_CONFIG.get(nombre_db)

    if path is None:
        raise ValueError(
            f"Base no configurada: {nombre_db}"
        )

    return str(path)


def get_db_connection(nombre_db):

    db_path = get_db_path(nombre_db)

    conn = sqlite3.connect(
        db_path,
        check_same_thread=False
    )

    conn.row_factory = sqlite3.Row

    return conn


# ==========================================
# ERP
# ==========================================

def get_erp_connection():
    return get_db_connection("erp")


# ==========================================
# MATERIALES
# ==========================================

def get_materiales_connection():
    return get_db_connection("materiales")


# ==========================================
# COMPRAS
# ==========================================

def get_compras_connection():
    return get_db_connection("compras")


# ==========================================
# INVENTARIOS
# ==========================================

def get_inventarios_connection():
    return get_db_connection("inventarios")


# ==========================================
# LOGISTICA
# ==========================================

def get_logistica_connection():
    return get_db_connection("logistica")


# ==========================================
# WMS
# ==========================================

def get_wms_connection():
    return get_db_connection("wms")
