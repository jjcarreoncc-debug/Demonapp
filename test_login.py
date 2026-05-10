import sqlite3
import pandas as pd

conn = sqlite3.connect("sigem.db")

print("ROLES")
print(
    pd.read_sql_query(
        "PRAGMA table_info(roles)",
        conn
    )
)

print("PERMISOS_ROLES")
print(
    pd.read_sql_query(
        "PRAGMA table_info(permisos_roles)",
        conn
    )
)

print("MODULOS")
print(
    pd.read_sql_query(
        "PRAGMA table_info(modulos)",
        conn
    )
)

conn.close()
