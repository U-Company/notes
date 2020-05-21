import os
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv
# from vault_client.client import VaultClient


def init_env_and_logger():
    APP_ENV = os.environ.get('APP_ENV', 'DEV')
    env = f"{APP_ENV}.env".lower()
    src_path = Path.cwd()
    path_file = src_path.joinpath('.deploy', '.envs', env)
    load_dotenv(path_file)
    cfg_env = os.environ
    cfg = dict()
    cfg['env'] = env
    cfg['stage'] = APP_ENV.lower()
    service_name = "SERVICES_INFO"
    cfg["service"] = service_name.lower()
    cfg['log_file'] = os.environ.get(f"SERVICE_{service_name}_LOG_FILE", "services_info")
    cfg['log_file'] = src_path.joinpath('logs', cfg['log_file'])

    cfg['base_name'] = os.environ.get(f"SERVICE_{service_name}_BASE_NAME", "services_info_dev")
    cfg['table_name'] = os.environ.get(f"SERVICE_{service_name}_BASE_NAME", "services_dev")

    logger.info(f"SERVICE: {service_name}")
    logger.info(f"APP_ENV: {APP_ENV}")
    logger.info(f"cfg_env: {env}")

    cfg['log_level'] = os.environ.get(f"SERVICE_{service_name}_LOG_LEVEL", "INFO")
    log_level_list = cfg['log_level'].split(",")
    if len(log_level_list) > 1:
        serialize = True
    else:
        serialize = False
    cfg['log_level'] = log_level_list[0]
    logger.add(cfg['log_file'], level=cfg['log_level'], serialize=serialize)
    cfg["logger"] = logger
    # # logger.add(sys.stderr, level=log_level, serialize=serialize)
    #
    #
    # logger.info(f"Service {course_creator_service}: host: {course_creator_host}  port: {course_creator_port}")
    # logger.info(f"Service {course_creator_service}: src_path: {src_path}  log_file_name: {log_file_name}")
    logger.info(f"Service {service_name}: log_level: {cfg['log_level']}  serialize: {serialize}")
    cfg['service_port'] = os.environ.get(f"SERVICE_{service_name}_PORT", 50100)

    cfg['service_host'] = os.environ.get(f"SERVICE_{service_name}_HOST", "0.0.0.0")

    #
    # storage_service = "STORAGE"
    # storage_port = client.get(storage_service, "port")
    # assert storage_port is not None, f"Service {storage_service} port not set."
    #
    # storage_host = client.get(storage_service, "host")
    # assert storage_host is not None, f"Service {storage_service} host not set."
    #
    # storage_schema = client.get(storage_service, "schema")
    # assert storage_schema is not None, f"Service {storage_service} schema not set."
    #
    # logger.info(f"Service {storage_service}: host: {storage_host}  port: {storage_port}")
    #
    # parser_service = "PARSER"
    # parser_port = client.get(parser_service, "port")
    # assert parser_port is not None, f"Service {parser_service}  port not set."
    #
    # parser_host = client.get(parser_service, "host")
    # assert parser_host is not None, f"Service {parser_service}  host not set."
    #
    # parser_schema = client.get(parser_service, "schema")
    # assert parser_schema is not None, f"Service {parser_service}  schema not set."
    return cfg
    # return {"logger": logger,
    #         "service": service_name,
    #         "stage": APP_ENV,
    #         "service_port": service_port,
    #         "service_host": service_host,
    #         # "course_creator_host": course_creator_host, "course_creator_port": course_creator_port,
    #         # "course_creator_schema": course_creator_schema,
    #         # "course_creator_token": course_creator_token,
    #         # "parser_port": parser_port, "parser_host": parser_host, "parser_schema": parser_schema,
    #         # "storage_port": storage_port, "storage_host": storage_host, "storage_schema": storage_schema,
    #         }