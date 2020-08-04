import aiohttp
import fastapi
import uvicorn
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleExportSpanProcessor,
    BatchExportSpanProcessor,
)
from opentelemetry.ext import jaeger
from opentelemetry.fastapi.utils import get_param

jaeger_host, server1_port, server2_port = get_param()

app = fastapi.FastAPI()

trace.set_tracer_provider(TracerProvider())

# trace.get_tracer_provider().add_span_processor(
#     BatchExportSpanProcessor(ConsoleSpanExporter())
# )
# create a JaegerSpanExporter
jaeger_exporter = jaeger.JaegerSpanExporter(
    service_name='fastapi_opentelemetry_server2',
    # configure agent
    agent_host_name=jaeger_host,
    agent_port=6831,
    # optional: configure also collector
    # collector_host_name='localhost',
    # collector_port=14268,
    # collector_endpoint='/api/traces?format=jaeger.thrift',
    # username=xxxx, # optional
    # password=xxxx, # optional
)

# Create a BatchExportSpanProcessor and add the exporter to it
span_processor = BatchExportSpanProcessor(jaeger_exporter)

# add to the tracer
trace.get_tracer_provider().add_span_processor(span_processor)



@app.get("/server_request")
async def server_request(param: str):
    print(f"param: {param}")
    return "Good served server 2"

FastAPIInstrumentor.instrument_app(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=server2_port)
