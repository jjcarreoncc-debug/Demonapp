import streamlit as st
import pandas as pd

from logistica_utils import limpiar_columnas, buscar_columna


# =========================
# ANALÍTICA LOGÍSTICA
# =========================
def logistica_analitica_app(
    transito,
    recepcion,
    despachos,
    transportistas,
    rutas
):

    st.title("📈 Analítica Logística")

    transito = limpiar_columnas(transito)
    recepcion = limpiar_columnas(recepcion)
    despachos = limpiar_columnas(despachos)
    transportistas = limpiar_columnas(transportistas)
    rutas = limpiar_columnas(rutas)

    tab1, tab2, tab3 = st.tabs([
        "📈 Tendencias",
        "💰 Costos",
        "🏆 Rankings"
    ])

    # =========================
    # COLUMNAS
    # =========================
    col_fecha_salida = buscar_columna(
        transito,
        ["FECHA_SALIDA", "FECHA SALIDA"]
    )

    col_fecha_despacho = buscar_columna(
        despachos,
        ["FECHA_DESPACHO", "FECHA DESPACHO"]
    )

    col_fecha_recepcion = buscar_columna(
        recepcion,
        ["FECHA_RECEPCION", "FECHA RECEPCION"]
    )

    col_estado_transito = buscar_columna(
        transito,
        ["ESTADO_TRANSITO", "ESTADO TRANSITO", "ESTADO"]
    )

    col_transportista = buscar_columna(
        transito,
        ["ID_TRANSPORTISTA", "TRANSPORTISTA"]
    )

    col_costo_flete = buscar_columna(
        transportistas,
        ["COSTO_FLETE", "COSTO FLETE"]
    )

    col_nombre_transportista = buscar_columna(
        transportistas,
        ["NOMBRE_TRANSPORTISTA", "NOMBRE TRANSPORTISTA", "TRANSPORTISTA"]
    )

    col_costo_ruta = buscar_columna(
        rutas,
        ["COSTO_ESTIMADO", "COSTO ESTIMADO"]
    )

    col_ruta_origen = buscar_columna(
        rutas,
        ["CIUDAD_ORIGEN", "ORIGEN"]
    )

    col_ruta_destino = buscar_columna(
        rutas,
        ["CIUDAD_DESTINO", "DESTINO"]
    )

    # =========================
    # TAB 1 - TENDENCIAS
    # =========================
    with tab1:

        st.subheader("📈 Tendencias operativas")

        if col_fecha_salida is not None:
            transito[col_fecha_salida] = pd.to_datetime(
                transito[col_fecha_salida],
                errors="coerce"
            )

            tendencia_transito = (
                transito
                .dropna(subset=[col_fecha_salida])
                .groupby(transito[col_fecha_salida].dt.date)
                .size()
                .reset_index(name="Tránsitos")
            )

            tendencia_transito.columns = ["Fecha", "Tránsitos"]

            st.write("🚛 Tránsitos por fecha")
            st.line_chart(
                tendencia_transito,
                x="Fecha",
                y="Tránsitos"
            )
        else:
            st.warning("No se encontró columna FECHA_SALIDA.")

        if col_fecha_despacho is not None:
            despachos[col_fecha_despacho] = pd.to_datetime(
                despachos[col_fecha_despacho],
                errors="coerce"
            )

            tendencia_despachos = (
                despachos
                .dropna(subset=[col_fecha_despacho])
                .groupby(despachos[col_fecha_despacho].dt.date)
                .size()
                .reset_index(name="Despachos")
            )

            tendencia_despachos.columns = ["Fecha", "Despachos"]

            st.write("📤 Despachos por fecha")
            st.line_chart(
                tendencia_despachos,
                x="Fecha",
                y="Despachos"
            )
        else:
            st.warning("No se encontró columna FECHA_DESPACHO.")

        if col_fecha_recepcion is not None:
            recepcion[col_fecha_recepcion] = pd.to_datetime(
                recepcion[col_fecha_recepcion],
                errors="coerce"
            )

            tendencia_recepcion = (
                recepcion
                .dropna(subset=[col_fecha_recepcion])
                .groupby(recepcion[col_fecha_recepcion].dt.date)
                .size()
                .reset_index(name="Recepciones")
            )

            tendencia_recepcion.columns = ["Fecha", "Recepciones"]

            st.write("📥 Recepciones por fecha")
            st.line_chart(
                tendencia_recepcion,
                x="Fecha",
                y="Recepciones"
            )
        else:
            st.warning("No se encontró columna FECHA_RECEPCION.")

    # =========================
    # TAB 2 - COSTOS
    # =========================
    with tab2:

        st.subheader("💰 Análisis de costos")

        if col_costo_flete is not None:
            costo_total = pd.to_numeric(
                transportistas[col_costo_flete],
                errors="coerce"
            ).fillna(0).sum()
        else:
            costo_total = 0

        if col_costo_ruta is not None:
            costo_promedio_ruta = pd.to_numeric(
                rutas[col_costo_ruta],
                errors="coerce"
            ).mean()

            if pd.isna(costo_promedio_ruta):
                costo_promedio_ruta = 0
        else:
            costo_promedio_ruta = 0

        c1, c2 = st.columns(2)

        c1.metric(
            "💰 Costo total fletes",
            f"${costo_total:,.0f}"
        )

        c2.metric(
            "🛣️ Costo promedio ruta",
            f"${costo_promedio_ruta:,.2f}"
        )

        if col_nombre_transportista is not None and col_costo_flete is not None:
            costos_transportista = (
                transportistas
                .groupby(col_nombre_transportista)[col_costo_flete]
                .sum()
                .reset_index()
                .sort_values(col_costo_flete, ascending=False)
                .head(10)
            )

            costos_transportista.columns = ["Transportista", "Costo"]

            st.write("🚚 Top costos por transportista")
            st.bar_chart(
                costos_transportista,
                x="Transportista",
                y="Costo"
            )
        else:
            st.warning("No se encontraron columnas para costo por transportista.")

        if col_costo_ruta is not None:
            rutas_tmp = rutas.copy()

            if col_ruta_origen is not None and col_ruta_destino is not None:
                rutas_tmp["RUTA"] = (
                    rutas_tmp[col_ruta_origen].astype(str)
                    + " → "
                    + rutas_tmp[col_ruta_destino].astype(str)
                )
            else:
                rutas_tmp["RUTA"] = rutas_tmp.index.astype(str)

            costos_ruta = (
                rutas_tmp[["RUTA", col_costo_ruta]]
                .copy()
                .sort_values(col_costo_ruta, ascending=False)
                .head(10)
            )

            costos_ruta.columns = ["Ruta", "Costo"]

            st.write("🛣️ Top rutas más costosas")
            st.bar_chart(
                costos_ruta,
                x="Ruta",
                y="Costo"
            )

    # =========================
    # TAB 3 - RANKINGS
    # =========================
    with tab3:

        st.subheader("🏆 Rankings operativos")

        if col_estado_transito is not None and col_transportista is not None:

            retrasados = transito[
                transito[col_estado_transito]
                .astype(str)
                .str.upper()
                .str.strip() == "RETRASADO"
            ]

            if len(retrasados) > 0:
                ranking_retrasos = (
                    retrasados[col_transportista]
                    .astype(str)
                    .value_counts()
                    .head(10)
                    .reset_index()
                )

                ranking_retrasos.columns = ["Transportista", "Retrasos"]

                st.write("🔴 Top transportistas con retrasos")
                st.bar_chart(
                    ranking_retrasos,
                    x="Transportista",
                    y="Retrasos"
                )
            else:
                st.success("No hay tránsitos retrasados.")
        else:
            st.warning("No se encontraron columnas para ranking de retrasos.")

        if col_estado_transito is not None:
            estados = (
                transito[col_estado_transito]
                .astype(str)
                .str.upper()
                .str.strip()
                .value_counts()
                .reset_index()
            )

            estados.columns = ["Estado", "Cantidad"]

            st.write("📊 Distribución de estados de tránsito")
            st.bar_chart(
                estados,
                x="Estado",
                y="Cantidad"
            )
