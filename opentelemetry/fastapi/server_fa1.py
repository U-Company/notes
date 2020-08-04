import aiohttp
# import fastapi
from fastapi import FastAPI, Header, HTTPException, Body, status
from fastapi.responses import JSONResponse
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
from opentelemetry.ext.aiohttp_client import create_trace_config

from opentelemetry.fastapi.utils import get_param
jaeger_host, server1_port, server2_port = get_param()
app = FastAPI()

trace.set_tracer_provider(TracerProvider())

# trace.get_tracer_provider().add_span_processor(
#     BatchExportSpanProcessor(ConsoleSpanExporter())
# )
# create a JaegerSpanExporter
jaeger_exporter = jaeger.JaegerSpanExporter(
    service_name='fastapi_opentelemetry_server1',
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


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.json(), response.status


async def get_url(url):
    async with aiohttp.ClientSession() as session:
        out_data, status = await fetch(session, url)
        return out_data, status


@app.get("/server_request")
async def read_main(param: str):
    print(f"Param: {param}")
    if param == "testing":
        return "Good server 1"
    else:
        url = f"http://localhost:{server2_port}/server_request?param={param}_2"
        async with aiohttp.ClientSession(trace_configs=[create_trace_config()]) as session:
            async with session.get(url) as response:
                txt = await response.text()
                if response.status == status.HTTP_200_OK:
                    content = {"param1": param, "answer": txt}
                    return JSONResponse(status_code=status.HTTP_201_CREATED, content=content)
                else:
                    content = {"param1": param, "answer": f"Error service 2: {txt} status: {response.status}"}
                    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=content)


FastAPIInstrumentor.instrument_app(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=server1_port)
