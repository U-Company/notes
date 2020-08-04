import aiohttp
from fastapi import FastAPI,status
from fastapi.responses import JSONResponse
import uvicorn
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.ext.aiohttp_client import create_trace_config

from opentelemetry.fastapi.utils import get_param
from opentelemetry.fastapi.ot_utils import init_jaeger

jaeger_host, server1_port, server2_port = get_param()
init_jaeger(jaeger_host, 'fastapi_opentelemetry_server1')

app = FastAPI()
FastAPIInstrumentor.instrument_app(app)


@app.get("/server_request")
async def read_main(param: str):
    print(f"Param: {param}")
    if param == "testing":
        return "Good server 1"
    else:
        url = f"http://localhost:{server2_port}/server_request?param={param}"
        async with aiohttp.ClientSession(trace_configs=[create_trace_config()]) as session:
            async with session.get(url) as response:
                txt = await response.text()
                if response.status == status.HTTP_200_OK:
                    content = {"param1": param, "answer": txt}
                    return JSONResponse(status_code=status.HTTP_201_CREATED, content=content)
                else:
                    content = {"param1": param, "answer": f"Error service 2: {txt} status: {response.status}"}
                    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=content)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(server1_port))
