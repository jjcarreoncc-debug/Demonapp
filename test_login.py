st.subheader("👥 Usuarios")

usuarios = pd.read_sql_query(
    "SELECT id_usuario, usuario, nombre, estado FROM usuarios",
    conn
)

st.dataframe(usuarios, use_container_width=True)
