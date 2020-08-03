from typing import List
import time

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import HTTPException
from fastapi import Depends, Request
import logging

# opentracing --------
from jaeger_client import Config as jaeger_config
from opentracing.scope_managers.contextvars import ContextVarsScopeManager
from opentracing_instrumentation.client_hooks import install_all_patches
from opentracing.ext import tags
from opentracing.propagation import Format

from starlette_opentracing import StarletteTracingMiddleWare

# opentracing ===============

# opentelemetry ----------
from opentelemetry import trace
from opentelemetry.ext import jaeger
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleExportSpanProcessor
from opentelemetry.ext.opentracing_shim import create_tracer

from opentelemetry.ext.sqlalchemy import SQLAlchemyInstrumentor

# opentelemetry ==========

from fastapi import FastAPI
import uvicorn

from app.internal.auth_utils import authenticate_user, make_token_for_user, Token, SECRET_KEY, get_current_user
from app.internal.db_utils import create_table, DB_PASS, DB_USER, DB_NAME, DB_HOST

from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST
from starlette.status import HTTP_200_OK, HTTP_201_CREATED
from starlette.responses import JSONResponse

import version
import app.internal.utils as utils
from service_client.db import init_db, all_services, add_service, Service as Db_service, get_service_by_name_stage,\
    deactivate_service, activate_service

service_name = f"{version.app_name} v.{version.app_version}"

cfg = utils.init_env_and_logger()
logger = cfg['logger']

logging.getLogger('').handlers = []
logging.basicConfig(format='%(message)s', level=logging.DEBUG)

app = FastAPI()

# Добавить реализцию для OpenTracing Shim for OpenTelemetry

# Tell OpenTelemetry which Tracer implementation to use.
trace.set_tracer_provider(TracerProvider())

jaeger_exporter = jaeger.JaegerSpanExporter(
    service_name=f"{service_name}_opentelemetry", agent_host_name="192.168.10.127", agent_port=6831
)

trace.get_tracer_provider().add_span_processor(
    SimpleExportSpanProcessor(jaeger_exporter)
)
# Create an OpenTelemetry Tracer.
# otel_tracer = trace.get_tracer(service_name)

# Create an OpenTracing shim.
# shim = create_tracer(otel_tracer)
shim = create_tracer(trace.get_tracer_provider())

# =========


# Добавить реализцию для opentracing
opentracing_config = jaeger_config(
    config={
        "sampler": {"type": "const", "param": 1},
        "logging": True,
        "local_agent": {"reporting_host": "localhost"},
    },
    scope_manager=ContextVarsScopeManager(),
    service_name= f"{service_name}_opentracing",
)
tracer_opentracing = opentracing_config.initialize_tracer()
install_all_patches()
app.add_middleware(StarletteTracingMiddleWare, tracer=shim)             # Использовать opentelemetry
app.add_middleware(StarletteTracingMiddleWare, tracer=tracer_opentracing)      # Использовать opentracing

# =========


class ServiceIn(BaseModel):
    name: str
    stage: str
    host: str
    port: int
    active: bool


class Service(BaseModel):
    id: int
    name: str
    stage: str
    host: str
    port: int
    active: bool



session, service_table, engine, database = init_db(DB_HOST, cfg["base_name"], DB_USER, DB_PASS, cfg["table_name"])

SQLAlchemyInstrumentor().instrument(
    engine=engine,
    service=service_name,
)



@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = await make_token_for_user(user, SECRET_KEY)
    return token


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*', "localhost", f"{cfg['service_host']}:{cfg['service_port']}", ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
async def root():
    return {"message": f"Hello from OpenTacing and OpenTelemetry demo app. app name: {version.app_name} "
                       f"V.{version.app_version}  {cfg['stage']}"}


@app.get("/ProcessHTTPRequestOpenTelemetry")
async def httprequestopentelemetry():
    with shim.start_active_span("ProcessHTTPRequestTelemetry"):
        print("Processing HTTP request (OpenTelemetry)")
        logger.info("Processing HTTP request (OpenTelemetry)")
        # Sleeping to mock real work.
        time.sleep(0.1)
        with shim.start_active_span("GetDataFromDB (Emulated) (OpenTelemetry)"):
            print("Getting data from DB (OpenTelemetry)")
            logger.info("Getting data from DB (OpenTelemetry)")
            # Sleeping to mock real work.
            time.sleep(0.2)

    return {"message": f"OpenTracing and OpenTelemetry (OpenTelemetry)."}


@app.get("/ProcessHTTPRequestOpenTracing")
async def httprequestopentracing():
    hello_to = "OpenTracing"
    with tracer_opentracing.start_span('say-hello') as span:
        span.set_tag('hello-to', hello_to)
        hello_str = 'Hello, %s!' % hello_to
        span.log_kv({'event': 'string-format', 'value': hello_str})

        print(hello_str)
        span.log_kv({'event': 'println'})
    return {"message": f"OpenTracing and OpenTelemetry (OpenTracing)."}


@app.get("/ProcessHTTPRequest")
async def httprequest():
    return {"message": f"OpenTracing and OpenTelemetry (httprequest)."}


def say_hello(hello_to):
    with tracer_opentracing.start_active_span('say-hello') as scope:
        scope.span.set_tag('hello-to', hello_to)
        scope.span.log_kv({'event': 'string-format', 'value': hello_to})

        hello_str = format_string(hello_to)
        print_hello(hello_str)


def format_string(hello_to):
    with tracer_opentracing.start_active_span('format') as scope:
        hello_str = 'Hello, %s!' % hello_to
        scope.span.log_kv({'event': 'format'})
        scope.span.log_kv({'event': 'string-format', 'value': hello_str})
        return hello_str


def print_hello(hello_str):
    with tracer_opentracing.start_active_span('println') as scope:
        print(hello_str)
        scope.span.log_kv({'event': 'println'})
        scope.span.log_kv({'event': 'string-format', 'value': hello_str})


@app.get("/format")
def format(request: Request):
    rq = request
    logger.debug(f"{rq}")
    span_ctx = tracer_opentracing.extract(Format.HTTP_HEADERS, request.headers)
    span_tags = {tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER}
    with tracer_opentracing.start_active_span('format', child_of=span_ctx, tags=span_tags):
        hello_to = request.query_params.get('helloTo')
        return 'Hello, %s!' % hello_to


@app.get("/publish")
def publish(request: Request):
    logger.debug(f"{request}")
    span_ctx = tracer_opentracing.extract(Format.HTTP_HEADERS, request.headers)
    span_tags = {tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER}
    with tracer_opentracing.start_active_span('publish', child_of=span_ctx, tags=span_tags):
        hello_str = request.query_params.get('helloStr')
        print(hello_str)
        return 'published'


@app.get("/helloopentracing")
async def helloopentracing():
    hello_to = "OpenTracing"
    say_hello(hello_to)
    return {"message": f"OpenTracing and OpenTelemetry (OpenTracing)."}


class Message(BaseModel):
    message: str


@app.get('/users', status_code=HTTP_200_OK)
async def users(user_password_hash: str = Depends(get_current_user)):
    return JSONResponse(status_code=HTTP_200_OK, content=user_password_hash)


@app.get("/service/", response_model=List[Service])
async def read_services(user_password_hash: str = Depends(get_current_user)):
    logger.info("123")
    services = all_services(session, service_table)
    return JSONResponse(status_code=HTTP_200_OK, content=services)


@app.get("/service/{name}/{stage}", response_model=List[Service])
async def read_services_by_name_stage(name: str, stage: str, user_password_hash: str = Depends(get_current_user)):
    services = get_service_by_name_stage(session, name, stage)
    if len(services):
        items = services[0].__dict__
        items.pop('_sa_instance_state', None)
    else:
        items = list()
    return JSONResponse(status_code=HTTP_200_OK, content=items)


@app.post("/service/", response_model=Service)
async def create_service(service_in: ServiceIn, user_password_hash: str = Depends(get_current_user)):
    serv = Db_service(service_in.name, service_in.stage, service_in.host, service_in.port, service_in.active)
    ok, error = add_service(session, serv)
    if ok:
        return JSONResponse(status_code=HTTP_201_CREATED, content="Service created")
    else:
        error_content = {
                "success": False,
                "data": {
                    "name": "Ошибка создания сервиса",
                    "message": error.orig.args[1],
                    "code": error.orig.args[0],
                    "status": HTTP_400_BAD_REQUEST,
                    "params": error.params,
                }
            }

        return JSONResponse(status_code=HTTP_400_BAD_REQUEST, content=error_content)


@app.patch("/service/{name}/{stage}/{active}", response_model=Service)
async def update_service(name: str, stage: str, active: bool, user_password_hash: str = Depends(get_current_user)):
    if active:
        ok, error = activate_service(session, name, stage)
        if error:
            message = "активирован"
        else:
            message = "состояние не изменилось"
    else:
        ok, error = deactivate_service(session, name, stage)
        if error:
            message = "деактивирован"
        else:
            message = "состояние не изменилось"
    if ok:

        content = {
                "success": True,
                "data": {
                    "name": "Активация сервиса",
                    "message": message,
                    "code": HTTP_200_OK,
                    "status": HTTP_200_OK,
                    "params": None,
                }
        }
        status_code = HTTP_200_OK
    else:
        content = {
                "success": False,
                "data": {
                    "name": "Активация сервиса",
                    "message": error.orig.args[1],
                    "code": error.orig.args[0],
                    "status": HTTP_400_BAD_REQUEST,
                    "params": error.params,
                }
            }
        status_code = HTTP_400_BAD_REQUEST
    return JSONResponse(status_code=status_code, content=content)


if __name__ == "__main__":
    logger.info(f"Start {cfg['service']}  {cfg['stage']}  v.{version.app_version}")
    uvicorn.run(app, host=f"{cfg['service_host']}", port=int(cfg['service_port']))
