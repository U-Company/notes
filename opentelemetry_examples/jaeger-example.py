from opentelemetry import trace
from opentelemetry.ext import jaeger
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleExportSpanProcessor

trace.set_tracer_provider(TracerProvider())

jaeger_exporter = jaeger.JaegerSpanExporter(
    service_name="my-helloworld-service", agent_host_name="localhost", agent_port=6831
)

trace.get_tracer_provider().add_span_processor(
    SimpleExportSpanProcessor(jaeger_exporter)
)
tracer = trace.get_tracer(__name__)
with tracer.start_as_current_span('foo'):
    with tracer.start_as_current_span('bar'):
        with tracer.start_as_current_span('baz'):
            print("Hello world from OpenTelemetry Python!")