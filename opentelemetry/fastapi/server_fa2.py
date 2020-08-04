import fastapi
from fastapi.responses import JSONResponse
import uvicorn
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.fastapi.utils import get_param

from opentelemetry.fastapi.ot_utils import init_jaeger

jaeger_host, server1_port, server2_port = get_param()
init_jaeger(jaeger_host, 'fastapi_opentelemetry_server2')

app = fastapi.FastAPI()
FastAPIInstrumentor.instrument_app(app)


@app.get("/server_request")
async def server_request(param: str):
    print(f"param: {param}")
    if "error" in param:
        return JSONResponse(status_code=500, content={"message": f"Error in param: {param}"})
    else:
        return "Good served server 2"


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(server2_port))
