import pytest

from service_client.db import init_db, all_services, add_service, Service, activate_service, deactivate_service
from service_client.db import get_service_by_host_port, get_service_by_name_stage
import service_client.db as db

DB_PASS = "222456"
DB_USER = "admin_urvanov"
DB_HOST = "192.168.10.13"
DB_NAME = "all_services"

table_prod = "service_prod"
table_dev = "service_dev"
table_stage = "service_stage"
table_test = "service_test"

session, service_table = init_db(DB_HOST, DB_NAME, DB_USER, DB_PASS, table_test)


def test_get_services():
    db.clear_services(session, service_table)
    services = all_services(session, service_table)
    assert len(services) == 0


def test_clear_services():
    db.clear_services(session, service_table)
    services = all_services(session, service_table)
    assert len(services) == 0


def test_add_service():
    serv = Service("service1", "prod", "127.0.0.1", 50001,  False)
    db.clear_services(session, service_table)
    ok = add_service(session, serv)
    assert ok
    services = all_services(session, service_table)
    assert len(services) == 1


def test_add_3service():
    serv1 = Service("service1", "prod", "127.0.0.1", 50001,  False)
    serv2 = Service("service2", "prod", "127.0.0.1", 50002,  True)
    serv3 = Service("service3", "prod", "127.0.0.1", 50003,  False)
    db.clear_services(session, service_table)
    ok = add_service(session, [serv1, serv2, serv3])
    assert ok
    services = all_services(session, service_table)
    assert len(services) == 3


def test_duplicated_service_ip_port():
    serv1 = Service("service1", "prod", "127.0.0.1", 50001,  False)
    serv2 = Service("service2", "prod", "127.0.0.1", 50002,  True)
    serv3 = Service("service3", "prod", "127.0.0.1", 50001,  False)
    db.clear_services(session, service_table)
    ok, error = add_service(session, [serv1, serv2, serv3])
    assert not ok
    assert error.orig.args[0] == 1062
    assert "Duplicate" in error.orig.args[1]


def test_duplicated_service_name_stage():
    serv1 = Service("service1", "prod", "127.0.0.1", 50001,  False)
    serv2 = Service("service2", "prod", "127.0.0.1", 50002,  True)
    serv3 = Service("service1", "prod", "127.0.0.1", 50003,  False)
    db.clear_services(session, service_table)
    ok, error = add_service(session, [serv1, serv2, serv3])
    assert not ok
    assert error.orig.args[0] == 1062
    assert "Duplicate" in error.orig.args[1]


def test_activate_service():
    serv1 = Service("service1", "prod", "127.0.0.1", 50001,  False)
    serv2 = Service("service3", "prod", "127.0.0.1", 50002,  True)
    serv3 = Service("service4", "prod", "127.0.0.1", 50003,  False)
    db.clear_services(session, service_table)
    ok = add_service(session, [serv1, serv2, serv3])
    assert ok
    services = all_services(session, service_table)
    assert len(services) == 3
    ok, error = activate_service(session, "service1", "prod")
    assert ok
    service1 = get_service_by_host_port(session, "127.0.0.1", 50002)
    assert len(service1) == 1
    assert service1[0].active


def test_deactivate_service():
    serv1 = Service("service1", "prod", "127.0.0.1", 50001,  False)
    serv2 = Service("service3", "prod", "127.0.0.1", 50002,  True)
    serv3 = Service("service4", "prod", "127.0.0.1", 50003,  False)
    db.clear_services(session, service_table)
    ok = add_service(session, [serv1, serv2, serv3])
    assert ok
    services = all_services(session, service_table)
    assert len(services) == 3
    ok, error = deactivate_service(session, "service1", "prod")
    assert ok
    service1 = get_service_by_name_stage(session, "service1", "prod")
    assert len(service1) == 1
    assert not service1[0].active


def test_get_service_by_host_port():
    serv1 = Service("service1", "prod", "127.0.0.1", 50001,  False)
    serv2 = Service("service3", "prod", "127.0.0.1", 50002,  True)
    serv3 = Service("service4", "prod", "127.0.0.1", 50003,  False)
    db.clear_services(session, service_table)
    ok = add_service(session, [serv1, serv2, serv3])
    assert ok
    service1 = get_service_by_host_port(session, "127.0.0.1", 50002)
    assert len(service1) == 1
    assert service1[0].name == "service3"


def test_get_service_by_name_stage():
    serv1 = Service("service1", "prod", "127.0.0.1", 50001,  False)
    serv2 = Service("service3", "prod", "127.0.0.1", 50002,  True)
    serv3 = Service("service4", "prod", "127.0.0.1", 50003,  False)
    db.clear_services(session, service_table)
    ok = add_service(session, [serv1, serv2, serv3])
    assert ok
    service1 = get_service_by_name_stage(session, "service3", "prod")
    assert len(service1) == 1
    assert service1[0].name == "service3"

