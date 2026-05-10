elif ruta == "inventarios":

    from sidebar_inventarios import sidebar_inventarios

    transaccion_inv = sidebar_inventarios()

    st.write(transaccion_inv)
