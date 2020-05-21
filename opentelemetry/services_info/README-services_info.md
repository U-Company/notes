# services_info

Сервис позволяет добавлять в базу данных (SQLite) информацию о сервисах 
(наименование, адрес, порт, stage, состояние (активный/неактивный)), просматривать сведения о сервисах,
активировать/деактивировать сервисы.  
 Для запуска сервиса следует перейти в папку ***service_info***.  
 - Активировать окружение Python
 - Установить зависимости:
    > ***make deps***  
 - Запустить сервис: 
    > ***python main.py***  
 
## Конфигурация сервиса

Файл с конфигурацией расположен в ***.deploy/.envs***, по умолчанию имя конфигурационного файла 
***dev.env***.  
Адрес сервиса (по умолчанию): ***localhost:40100***  
Для авторизации в сервисе следует ввести ввести имя и пароль (авторизация будет успешной при совпадении имени и пароля).  


## Попытка интеграции opentelemetry и opentracing

В текущем состоянии в проекте opentelemetry нет расширений или middleware для поддержки
ASGI. Для проекта Opentracing есть поддержка Starlette и FastAPI 
([проект Starlette-OpenTracing](https://pypi.org/project/Starlette-OpenTracing/)).  
В **opentelemetry** есть  расширение для миграции проектов с opentracing на opentelemetry
[OpenTracing Shim for OpenTelemetry](https://opentelemetry-python.readthedocs.io/en/latest/ext/opentracing_shim/opentracing_shim.html)

### Подключение **opentelemetry** и **opentracing**

Для подключения **opentelemetry** следует в main.py добавить (строки 55 - 72):

``` Python
# Tell OpenTelemetry which Tracer implementation to use.
trace.set_tracer_provider(TracerProvider())

jaeger_exporter = jaeger.JaegerSpanExporter(
    service_name=service_name, agent_host_name="localhost", agent_port=6831
)

trace.get_tracer_provider().add_span_processor(
    SimpleExportSpanProcessor(jaeger_exporter)
)
# Create an OpenTelemetry Tracer.
otel_tracer = trace.get_tracer(service_name)

# Create an OpenTracing shim.
# shim = create_tracer(otel_tracer)
shim = create_tracer(trace.get_tracer_provider())

# =========

```

Для подключения **opentracing** следует в main.py добавить (строки 76 - 90):

``` Python
opentracing_config = jaeger_config(
    config={
        "sampler": {"type": "const", "param": 1},
        "logging": True,
        "local_agent": {"reporting_host": "localhost"},
    },
    scope_manager=ContextVarsScopeManager(),
    service_name= service_name,
)
jaeger_tracer = opentracing_config.initialize_tracer()
install_all_patches()
# app.add_middleware(StarletteTracingMiddleWare, tracer=shim)             # Использовать opentelemetry
app.add_middleware(StarletteTracingMiddleWare, tracer=jaeger_tracer)      # Использовать opentracing

# =========
```

В строках 87 - 88 (в main.py) можно выбрать что использовать **opentelemetry** или **opentracing**:

``` Python
# app.add_middleware(StarletteTracingMiddleWare, tracer=shim)
app.add_middleware(StarletteTracingMiddleWare, tracer=jaeger_tracer)
```
Строка 87:
``` Python
app.add_middleware(StarletteTracingMiddleWare, tracer=shim)
```
подключает **opentelemetry**.

Строка 88:
``` Python
app.add_middleware(StarletteTracingMiddleWare, tracer=jaeger_tracer)
```
подключает **opentracing**.

Для просмотра трэйсов следует запустить Jaeger.  
Запуск docker-контейнера:  
> docker run -d --name jaeger \  
  -e COLLECTOR_ZIPKIN_HTTP_PORT=9411 \  
  -p 5775:5775/udp \  
  -p 6831:6831/udp \  
  -p 6832:6832/udp \  
  -p 5778:5778 \  
  -p 16686:16686 \  
  -p 14268:14268 \  
  -p 14250:14250 \  
  -p 9411:9411 \  
  jaegertracing/all-in-one:1.18  

Jaeger-ui будет доступен по адресу **localhost:16686**.

## Предварительные выводы.

- При использовании **opentracing** трэйсы энндпойнтов с опирациями с базой данных включают
в себя span-ы  работы с базой (SQL), при использовании **opentelemetry** - span-ы эндпойнтов - независимы.

- Необходимо сделать сервис на Flask для проверки интеграции серивсов с **opentelemetry** (т.к. есть в **opentelemetry**
уже есть **OpenTelemetry WSGI Middleware**,  **OpenTelemetry Flask Integration**) с сервисами с **opentracing**.







