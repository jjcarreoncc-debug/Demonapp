import sqlite3
import pandas as pd

conn = sqlite3.connect("sigem.db")

# ==========================================
# VER ESTRUCTURA TABLA USUARIOS
# ==========================================

estructura = pd.read_sql_query(
    "PRAGMA table_info(usuarios)",
    conn
)

print(estructura)

conn.close()
