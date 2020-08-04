import os
from dotenv import load_dotenv

def get_param():
    load_dotenv(dotenv_path=".env", encoding="utf-8")
    jaeger_host = os.getenv("jaeger_host")
    server1_port = os.getenv("server1_port")
    server2_port = os.getenv("server2_port")
    return jaeger_host, server1_port, server2_port

