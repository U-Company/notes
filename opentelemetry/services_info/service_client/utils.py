def set_utf8_for_tables(session):
    tables = session.get_bind().table_names()
    for table in tables:
        session.execute(f"ALTER TABLE {table} CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;")
