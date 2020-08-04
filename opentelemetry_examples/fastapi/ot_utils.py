from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleExportSpanProcessor,
    BatchExportSpanProcessor,
)
from opentelemetry import trace

from opentelemetry.ext import jaeger

def init_jaeger(jaeger_host: str, service_name):
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer_provider().get_tracer(__name__)
    # trace.get_tracer_provider().add_span_processor(
    #     BatchExportSpanProcessor(ConsoleSpanExporter())
    # )
    # create a JaegerSpanExporter
    jaeger_exporter = jaeger.JaegerSpanExporter(
        service_name=service_name,
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
    return tracer
