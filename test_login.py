import sqlite3
import shutil
import os
import streamlit as st

from sigem_db import get_db_path


# =====================================================
# TABLAS DE SEGURIDAD
# =====================================================

TABLAS_SEGURIDAD = [

    "usuarios",
    "roles",
    "modulos",
    "permisos",
    "usuario_roles",
    "rol_permisos",
    "sesiones_usuario"

]


# =====================================================
# COPIAR TABLA
# =====================================================

def copiar_tabla(origen_db, destino_db, tabla):

    conn_origen = sqlite3.connect(origen_db)
    conn_destino = sqlite3.connect(destino_db)

    cur_origen = conn_origen.cursor()
    cur_destino = conn_destino.cursor()

    # =========================
    # LEER SQL ORIGINAL
    # =========================

    cur_origen.execute("""
        SELECT sql
        FROM sqlite_master
        WHERE type = 'table'
          AND name = ?
    """, (tabla,))

    row = cur_origen.fetchone()

    if row is None:

        conn_origen.close()
        conn_destino.close()

        raise Exception(
            f"La tabla {tabla} no existe en ERP."
        )

    sql_create = row[0]

    # =========================
    # ELIMINAR TABLA DESTINO
    # =========================

    cur_destino.execute(
        f"DROP TABLE IF EXISTS {tabla}"
    )

    # =========================
    # CREAR TABLA NUEVA
    # =========================

    cur_destino.execute(sql_create)

    # =========================
    # COPIAR DATOS
    # =========================

    cur_origen.execute(
        f"SELECT * FROM {tabla}"
    )

    filas = cur_origen.fetchall()

    columnas = [
        col[0]
        for col in cur_origen.description
    ]

    if filas:

        placeholders = ",".join(
            ["?"] * len(columnas)
        )

        columnas_sql = ",".join(columnas)

        cur_destino.executemany(
            f"""
            INSERT INTO {tabla} (
                {columnas_sql}
            )
            VALUES (
                {placeholders}
            )
            """,
            filas
        )

    conn_destino.commit()

    conn_origen.close()
    conn_destino.close()


# =====================================================
# APP TEST
# =====================================================

def copiar_tablas_seguridad_app():

    st.markdown(
        "## 🧪 Copiar tablas de seguridad"
    )

    st.caption(
        "Copia tablas buenas desde ERP hacia la base real del sistema."
    )

    # =========================
    # ORIGEN ERP
    # =========================

    origen_db = get_db_path("erp")

    # =========================
    # DESTINO REAL SIGEM
    # =========================

    destino_db = get_db_path("seguridad")

    st.info(f"📥 ERP origen: {origen_db}")

    st.info(f"📤 Destino SIGEM: {destino_db}")

    st.markdown(
        "### 📋 Tablas a copiar"
    )

    st.write(TABLAS_SEGURIDAD)

    confirmar = st.checkbox(
        "Confirmo reemplazar tablas de seguridad"
    )

    # =========================
    # COPIAR
    # =========================

    if st.button("📋 Copiar tablas"):

        if not confirmar:

            st.warning(
                "⚠️ Debes confirmar el proceso."
            )

            return

        try:

            # =========================
            # BACKUP
            # =========================

            backup_path = (
                destino_db + ".backup"
            )

            if os.path.exists(destino_db):

                shutil.copy2(
                    destino_db,
                    backup_path
                )

                st.success(
                    f"✅ Backup creado: {backup_path}"
                )

            # =========================
            # COPIAR TABLAS
            # =========================

            for tabla in TABLAS_SEGURIDAD:

                copiar_tabla(
                    origen_db,
                    destino_db,
                    tabla
                )

                st.success(
                    f"✅ Tabla copiada: {tabla}"
                )

            st.success(
                "✅ Proceso terminado correctamente."
            )

            st.info(
                "Ahora cambia seguridad para usar get_db_path('seguridad')"
            )

        except Exception as e:

            st.error(
                "❌ Error copiando tablas."
            )

            st.exception(e)


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    copiar_tablas_seguridad_app()
