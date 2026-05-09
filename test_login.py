st.subheader("📋 Roles")

roles = cursor.execute(
    """
    SELECT *
    FROM roles
    """
).fetchall()

st.write(roles)
