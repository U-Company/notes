import flask
import requests

import opentelemetry.ext.requests
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from opentelemetry.sdk.trace.export import SimpleExportSpanProcessor
from opentelemetry.ext.flask import FlaskInstrumentor

trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    SimpleExportSpanProcessor(ConsoleSpanExporter())
)

app = flask.Flask(__name__)
FlaskInstrumentor().instrument_app(app)
# opentelemetry.ext.http_requests.RequestsInstrumentor().instrument()
opentelemetry.ext.requests.RequestsInstrumentor().instrument()

@app.route("/")
def hello():
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("example-request"):
        requests.get("http://www.example.com")
    return "hello"

app.run(debug=True, port=5100)