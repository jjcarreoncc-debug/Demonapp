if st.button("Reset password admin a 1234"):

    cursor.execute(
        """
        UPDATE usuarios
        SET password_hash = ?,
            estado = 'Activo'
        WHERE usuario = 'admin'
        """,
        (hash_password("1234"),)
    )

    conn.commit()

    st.success("✅ Password de admin actualizado a 1234")
