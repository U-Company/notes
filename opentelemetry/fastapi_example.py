from fastapi import FastAPI
import uvicorn
from starlette.middleware.cors import CORSMiddleware
from loguru import logger

serialize = False
logger.add('log_file.log', level='DEBUG', serialize=serialize)
logger.info("123")

version = {"app_version": "0.1.0", "app_name": "FastAPI example"}
app = FastAPI()


host = "0.0.0.0"
port = 50000

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*', "localhost", f"{host}:{port}", ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
async def root():
    return {"message": f"Hello from  {version['app_name']}  V.{version['app_version']}"}


if __name__ == "__main__":
    logger.info(f"Start {version['app_name']}    v.{version['app_version']}")
    uvicorn.run(app, host=f"{host}", port=port)
