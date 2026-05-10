tablas = conn.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type='table'
""").fetchall()

st.write("TABLAS EN ESTA BD:")
for t in tablas:
    st.write(dict(t))
