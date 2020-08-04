# from typing import List
import databases
import sqlalchemy
from service_client.utils import set_utf8_for_tables
from sqlalchemy import UniqueConstraint
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import select, func, Integer, Table, Column, MetaData, String, Boolean
from sqlalchemy.orm import mapper
from loguru import logger

# from pydantic import BaseModel
# from app.internal.db_utils import set_utf8_for_tables
# SQLAlchemy specific code, as with any other app
from sqlalchemy.ext.declarative import declarative_base


# Base = declarative_base()
#
#
class Service(object):
    def __init__(self, name, stage, host, port, active):
        self.name = name
        self.stage = stage
        self.host = host
        self.port = port
        self.active = active


def init_db(host, db_name, user, password, table_name):
    database_url = f"mysql://{user}:{password}@{host}/{db_name}"
    database_url = f'sqlite:///{db_name}'
    # logger.debug(f"DB: {database_url}")
    database = databases.Database(database_url)

    metadata = sqlalchemy.MetaData()

    service_table = sqlalchemy.Table(
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
    mapper(Service, service_table)
    engine = sqlalchemy.create_engine(
        database_url
    )
    metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session_db = scoped_session(Session)

    # set_utf8_for_tables(session_db)
    return session_db, service_table, engine, database


def add_service(session, service):
    if isinstance(service, list):
        session.add_all(service)
    else:
        session.add(service)
    try:
        session.commit()
        added_services = True
    except SQLAlchemyError as e:
        logger.error(f"{e}")
        session.rollback()
        return False, e
    return added_services, None


def activate_service(session, service_name, service_stage):
    is_updated = session.query(Service).filter(Service.name == service_name, Service.stage == service_stage).update(dict(active=True))
    try:
        session.commit()
        service_activated = True
    except SQLAlchemyError as e:
        logger.error(f"{e}")
        session.rollback()
        return False, e
    return service_activated, is_updated


def deactivate_service(session, service_name, service_stage):
    is_updated = session.query(Service).filter(Service.name == service_name, Service.stage == service_stage).update(dict(active=False))
    try:
        session.commit()
        service_activated = True
    except SQLAlchemyError as e:
        logger.error(f"{e}")
        session.rollback()
        return False, e
    return service_activated, is_updated


def get_service_by_name_stage(session, service_name, service_stage):
    all_services = session.query(Service).filter(Service.name == service_name, Service.stage == service_stage).all()
    return all_services


def get_service_by_host_port(session, service_host, service_port):
    all_services = session.query(Service).filter(Service.host == service_host, Service.port == service_port).all()
    return all_services


def clear_services(session, table):
    session.execute(table.delete())
    session.commit()
    return


def asdict(row):
    result = dict()
    for key in row.keys():
        if getattr(row, key) is not None:
            result[key] = str(getattr(row, key))
        else:
            result[key] = getattr(row, key)
    return result


def all_services(session, table):
    result = session.query(table).all()
    all_recs = [asdict(row) for row in result]
    return all_recs