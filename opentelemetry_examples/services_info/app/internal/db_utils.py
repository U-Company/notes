import sys

import databases
import sqlalchemy
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import sessionmaker, scoped_session

DB_PASS = "222456"
DB_USER = "admin_urvanov"
DB_HOST = "192.168.10.13"
DB_NAME = "all_services"


def set_utf8_for_tables(session):
    # print(f"{__file__}  {sys._getframe().f_lineno}  {__name__}  ")
    tables = session.get_bind().table_names()
    for table in tables:
        if table != 'alembic_version':
            # print(f"{__file__}  {sys._getframe().f_lineno}  {__name__}  table: {table}")
            session.execute(
                f"ALTER TABLE {table} CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;")


def create_table(table_name):
    global DB_PASS, DB_USER, DB_HOST, DB_NAME, database, metadata, engine, Session
    # SQLAlchemy specific code, as with any other app
    DATABASE_URL ='sqlite:///:memory:'
    database = databases.Database(DATABASE_URL)
    metadata = sqlalchemy.MetaData()
    service = sqlalchemy.Table(
        table_name,
        metadata,
        sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
        sqlalchemy.Column("name", sqlalchemy.String(32)),
        sqlalchemy.Column("stage", sqlalchemy.String(10)),
        sqlalchemy.Column("host", sqlalchemy.String(32)),
        sqlalchemy.Column("port", sqlalchemy.Integer),
        sqlalchemy.Column("active", sqlalchemy.Boolean),
        UniqueConstraint('host', 'port', name='host_port'),
        UniqueConstraint('name', 'stage', name='name_stage'),
    )
    engine = sqlalchemy.create_engine(
        DATABASE_URL
    )
    metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session_db = scoped_session(Session)
    # set_utf8_for_tables(session_db)
    return database