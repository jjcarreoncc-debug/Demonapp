import sqlite3
import pandas as pd
from datetime import datetime
from io import BytesIO

from sigem_db import get_db_path


def obtener_columnas_tabla(conn, tabla):

    df_cols = pd.read_sql_query(
        f"PRAGMA table_info({tabla})",
        conn
    )

    return df_cols["name"].tolist()


def insertar_dinamico(conn, tabla, datos):

    columnas_tabla = obtener_columnas_tabla(conn, tabla)

    datos_filtrados = {
        k: v
        for k, v in datos.items()
        if k in columnas_tabla
    }

    if not datos_filtrados:
        return

    columnas = list(datos_filtrados.keys())
    placeholders = ",".join(["?"] * len(columnas))

    sql = f"""
        INSERT INTO {tabla} (
            {",".join(columnas)}
        )
        VALUES (
            {placeholders}
        )
    """

    valores = [datos_filtrados[col] for col in columnas]

    conn.execute(sql, valores)


def generar_folio_embarque():

    fecha = datetime.now().strftime("%Y%m%d%H%M%S")

    return f"EMB-{fecha}"


def obtener_detalle_hoja_carga(folio_hoja_carga):

    conn = sqlite3.connect(get_db_path("logistica"))

    query = """
        SELECT
            folio_hoja_carga,
            pedido,
            codigo_material,
            descripcion,
            cantidad_pedido,
            cantidad_surtida,
            bodega,
            ubicacion,
            peso,
            volumen,
            observaciones
        FROM detalle_hoja_carga
        WHERE folio_hoja_carga = ?
    """

    df = pd.read_sql_query(
        query,
        conn,
        params=[folio_hoja_carga]
    )

    conn.close()

    return df


def crear_notificacion_inventarios(conn, folio_embarque, hoja, transporte):

    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS notificaciones_inventarios (
            id_notificacion INTEGER PRIMARY KEY AUTOINCREMENT,
            folio_embarque TEXT,
            folio_hoja_carga TEXT,
            modulo_origen TEXT,
            tipo_notificacion TEXT,
            mensaje TEXT,
            estatus TEXT,
            fecha_creacion TEXT,
            usuario TEXT
        )
    """)

    mensaje = (
        f"Embarque {folio_embarque} pendiente de carga física. "
        f"Hoja carga: {hoja.get('folio_hoja_carga', '')}. "
        f"Transporte: {transporte.get('codigo_transporte', '')}."
    )

    conn.execute("""
        INSERT INTO notificaciones_inventarios (
            folio_embarque,
            folio_hoja_carga,
            modulo_origen,
            tipo_notificacion,
            mensaje,
            estatus,
            fecha_creacion,
            usuario
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        folio_embarque,
        hoja.get("folio_hoja_carga", ""),
        "Logística",
        "Carga embarque",
        mensaje,
        "Pendiente",
        fecha_actual,
        "admin"
    ))


def generar_excel_embarque(df_embarques, df_detalle, df_notificaciones):

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:

        df_embarques.to_excel(
            writer,
            sheet_name="Resumen embarque",
            index=False
        )

        df_detalle.to_excel(
            writer,
            sheet_name="Detalle materiales",
            index=False
        )

        df_notificaciones.to_excel(
            writer,
            sheet_name="Notificacion inventarios",
            index=False
        )

    output.seek(0)

    return output


def procesar_confirmacion_embarque(df_seleccionadas, transporte):

    conn = sqlite3.connect(get_db_path("logistica"))

    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    codigo_transporte = (
        f"TR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    )
    
    folios_creados = []
    registros_embarque = []
    registros_detalle = []
    registros_notificacion = []

    try:

        for i, hoja in df_seleccionadas.iterrows():

            folio_embarque = generar_folio_embarque() + f"-{i + 1}"

            datos_embarque = {
                "folio_embarque": folio_embarque,
                "folio_hoja_carga": hoja.get("folio_hoja_carga", ""),
                "folio_ruta": transporte.get("codigo_ruta", ""),
                "codigo_ruta": transporte.get("codigo_ruta", ""),
                "codigo_transporte": codigo_transporte,
                "pedido": hoja.get("pedido", ""),
                "fecha": fecha_actual,
                "cliente": hoja.get("cliente", ""),
                "destino": hoja.get("destino", ""),
                "transportista": transporte.get("transportista", ""),
                "vehiculo": transporte.get("vehiculo", ""),
                "placas": transporte.get("placas", ""),
                "operador": transporte.get("operador", ""),
                "ruta": transporte.get("codigo_ruta", ""),
                "estatus": "Pendiente carga",
                "fecha_estatus": fecha_actual,
                "usuario_estatus": "admin",
                "observaciones": "Embarque confirmado. Pendiente carga física por Inventarios.",
                "usuario": "admin",
                "fecha_creacion": fecha_actual
            }

            insertar_dinamico(
                conn,
                "embarques",
                datos_embarque
            )

            registros_embarque.append(datos_embarque)

            df_detalle = obtener_detalle_hoja_carga(
                hoja.get("folio_hoja_carga", "")
            )

            for _, det in df_detalle.iterrows():

                datos_detalle = {
                    "folio_embarque": folio_embarque,
                    "folio_hoja_carga": hoja.get("folio_hoja_carga", ""),
                    "folio_ruta": transporte.get("codigo_ruta", ""),
                    "pedido": det.get("pedido", hoja.get("pedido", "")),
                    "codigo_material": det.get("codigo_material", ""),
                    "descripcion": det.get("descripcion", ""),
                    "cantidad_pedida": det.get("cantidad_pedido", 0),
                    "cantidad_embarcar": det.get(
                        "cantidad_surtida",
                        det.get("cantidad_pedido", 0)
                    ),
                    "peso": det.get("peso", 0),
                    "volumen": det.get("volumen", 0),
                    "bodega": det.get("bodega", ""),
                    "ubicacion": det.get("ubicacion", "")
                }

                insertar_dinamico(
                    conn,
                    "detalle_embarque",
                    datos_detalle
                )

                registros_detalle.append(datos_detalle)

            crear_notificacion_inventarios(
                conn,
                folio_embarque,
                hoja,
                transporte
            )

            registros_notificacion.append({
                "folio_embarque": folio_embarque,
                "folio_hoja_carga": hoja.get("folio_hoja_carga", ""),
                "tipo_notificacion": "Carga embarque",
                "estatus": "Pendiente",
                "fecha_creacion": fecha_actual
            })

            folios_creados.append(folio_embarque)

        conn.commit()

    except Exception as e:

        conn.rollback()
        conn.close()
        raise e

    conn.close()

    df_embarques = pd.DataFrame(registros_embarque)
    df_detalle_final = pd.DataFrame(registros_detalle)
    df_notificaciones = pd.DataFrame(registros_notificacion)

    excel = generar_excel_embarque(
        df_embarques,
        df_detalle_final,
        df_notificaciones
    )

    return {
        "ok": True,
        "mensaje": "✅ Embarque confirmado y notificación enviada a Inventarios.",
        "folios": folios_creados,
        "df_embarques": df_embarques,
        "df_detalle": df_detalle_final,
        "df_notificaciones": df_notificaciones,
        "excel": excel
    }
