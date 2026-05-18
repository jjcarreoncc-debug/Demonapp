import sqlite3
import shutil
import os
import streamlit as st

from sigem_db import get_db_path


# =====================================================
# TABLAS VALIDAS EN ERP
# =====================================================

TABLAS_SEGURIDAD = [
    "usuarios",
    "roles",
    "modulos",
    "permisos_roles"
]


# =====================================================
# VALIDAR TABLA
# =====================================================

def tabla_existe(conn, tabla):

    cur = conn.cursor()

    cur.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name = ?
        """,
        (tabla,)
    )

    return cur.fetchone() is not None


# =====================================================
# COPIAR TABLA
# =====================================================

def copiar_tabla(
    origen_db,
    destino_db,
    tabla
):

    conn_origen = sqlite3.connect(origen_db)

    conn_destino = sqlite3.connect(destino_db)

    cur_origen = conn_origen.cursor()

    cur_destino = conn_destino.cursor()

    if not tabla_existe(
        conn_origen,
        tabla
    ):

        conn_origen.close()

        conn_destino.close()

        return False, (
            f"⚠️ La tabla {tabla} "
            f"no existe en ERP."
        )

    # =========================
    # OBTENER CREATE TABLE
    # =========================

    cur_origen.execute(
        """
        SELECT sql
        FROM sqlite_master
        WHERE type = 'table'
          AND name = ?
        """,
        (tabla,)
    )

    row = cur_origen.fetchone()

    sql_create = row[0]

    # =========================
    # RECREAR TABLA DESTINO
    # =========================

    cur_destino.execute(
        f"DROP TABLE IF EXISTS {tabla}"
    )

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

        columnas_sql = ", ".join(columnas)

        placeholders = ", ".join(
            ["?"] * len(columnas)
        )

        cur_destino.executemany(
            f"""
            INSERT INTO {tabla}
            (
                {columnas_sql}
            )
            VALUES
            (
                {placeholders}
            )
            """,
            filas
        )

    conn_destino.commit()

    conn_origen.close()

    conn_destino.close()

    return True, (
        f"✅ Tabla copiada: {tabla}"
        f" | Registros: {len(filas)}"
    )


# =====================================================
# VERIFICAR DESTINO
# =====================================================

def verificar_destino(destino_db):

    conn = sqlite3.connect(destino_db)

    cur = conn.cursor()

    cur.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
        """
    )

    tablas = [
        row[0]
        for row in cur.fetchall()
    ]

    resultado = {}

    for tabla in tablas:

        try:

            cur.execute(
                f"SELECT COUNT(*) FROM {tabla}"
            )

            resultado[tabla] = (
                cur.fetchone()[0]
            )

        except:

            resultado[tabla] = "ERROR"

    conn.close()

    return resultado


# =====================================================
# APP
# =====================================================

def copiar_seguridad_desde_erp_app():

    st.title(
        "🧪 Copiar Seguridad ERP → seguridad.db"
    )

    origen_db = get_db_path("erp")

    destino_db = get_db_path("seguridad")

    st.success(
        f"📥 ERP: {origen_db}"
    )

    st.success(
        f"📤 SEGURIDAD: {destino_db}"
    )

    st.markdown("### 📋 Tablas a copiar")

    st.write(TABLAS_SEGURIDAD)

    confirmar = st.checkbox(
        "Confirmo reemplazar seguridad.db"
    )

    if st.button(
        "🚀 Ejecutar copia",
        use_container_width=True
    ):

        if not confirmar:

            st.warning(
                "⚠️ Debes confirmar."
            )

            return

        try:

            # =========================
            # BACKUP
            # =========================

            if os.path.exists(
                destino_db
            ):

                backup = (
                    destino_db
                    + ".backup"
                )

                shutil.copy2(
                    destino_db,
                    backup
                )

                st.success(
                    f"✅ Backup: {backup}"
                )

            # =========================
            # COPIAR TABLAS
            # =========================

            for tabla in TABLAS_SEGURIDAD:

                ok, mensaje = copiar_tabla(
                    origen_db,
                    destino_db,
                    tabla
                )

                if ok:

                    st.success(mensaje)

                else:

                    st.warning(mensaje)

            # =========================
            # VALIDAR FINAL
            # =========================

            resumen = verificar_destino(
                destino_db
            )

            st.markdown(
                "### ✅ Resultado final"
            )

            st.json(resumen)

            st.success(
                "✅ Copia finalizada."
            )

        except Exception as e:

            st.error(
                "❌ Error copiando seguridad."
            )

            st.exception(e)


# =====================================================
# EJECUTAR
# =====================================================

if __name__ == "__main__":

    copiar_seguridad_desde_erp_app()
