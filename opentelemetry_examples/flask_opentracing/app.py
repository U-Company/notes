import requests
import sys
import time
import logging
import json

from flask import Flask, Blueprint, request, jsonify
from flask_restx import Api, Resource, fields

from lib.tracing import init_tracer
from opentracing.ext import tags
from opentracing.propagation import Format

log_level = logging.DEBUG
logging.getLogger('').handlers = []
logging.basicConfig(format='%(asctime)s %(message)s', level=log_level)

api_v1 = Blueprint("api", __name__, url_prefix="/api/1")
api = Api(api_v1, version="1.0", title="OpenTracing API", description="A simple OpenTracing API",)

ns = api.namespace("opentracing", description="OpenTracing operations")

TODOS = {
    "todo1": {"task": "build an API"},
    "todo2": {"task": "?????"},
    "todo3": {"task": "profit!"},
}

todo = api.model(
    "Todo", {"task": fields.String(required=True, description="The task details")}
)

listed_todo = api.model(
    "ListedTodo",
    {
        "id": fields.String(required=True, description="The todo ID"),
        "todo": fields.Nested(todo, description="The Todo"),
    },
)


def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in TODOS:
        api.abort(404, "Todo {} doesn't exist".format(todo_id))


parser = api.parser()
parser.add_argument(
    "task", type=str, required=True, help="The task details", location="form"
)


@ns.route("/<string:todo_id>")
@api.doc(responses={404: "Todo not found"}, params={"todo_id": "The Todo ID"})
class Todo(Resource):
    """Show a single todo item and lets you delete them"""

    @api.doc(description="todo_id should be in {0}".format(", ".join(TODOS.keys())))
    @api.marshal_with(todo)
    def get(self, todo_id):
        """Fetch a given resource"""
        abort_if_todo_doesnt_exist(todo_id)
        return TODOS[todo_id]

    @api.doc(responses={204: "Todo deleted"})
    def delete(self, todo_id):
        """Delete a given resource"""
        abort_if_todo_doesnt_exist(todo_id)
        del TODOS[todo_id]
        return "", 204

    @api.doc(parser=parser)
    @api.marshal_with(todo)
    def put(self, todo_id):
        """Update a given resource"""
        args = parser.parse_args()
        task = {"task": args["task"]}
        TODOS[todo_id] = task
        return task


@ns.route("/")
class TodoList(Resource):
    """Shows a list of all todos, and lets you POST to add new tasks"""

    @api.marshal_list_with(listed_todo)
    def get(self):
        """List all todos"""
        return [{"id": id, "todo": todo} for id, todo in TODOS.items()]

    @api.doc(parser=parser)
    @api.marshal_with(todo, code=201)
    def post(self):
        """Create a todo"""
        args = parser.parse_args()
        todo_id = "todo%d" % (len(TODOS) + 1)
        TODOS[todo_id] = {"task": args["task"]}
        return TODOS[todo_id], 201


tracer = init_tracer('flask_opentrasing')

host = "localhost"
port = 40100


def say_hello_opentracing(host, hello_to):
    with tracer.start_active_span('say-hello_opentracing') as scope:
        scope.span.set_tag('hello-to_opentracing', hello_to)
        hello_str = format_string_opentracing(host, hello_to)
        print_hello_opentracing(host, hello_str)


def format_string_opentracing(host, hello_to):
    with tracer.start_active_span(f'format_opentracing') as scope:
        hello_str = http_get_opentracing(host, port, 'format', 'helloTo', hello_to)
        scope.span.log_kv({'event': 'string-format', 'value': hello_str})
        return hello_str


def print_hello_opentracing(host, hello_str):
    with tracer.start_active_span('println_opentracing') as scope:
        http_get_opentracing(host, port, 'publish', 'helloStr', hello_str)
        scope.span.log_kv({'event': 'println'})


def http_get_opentracing(host, port, path, param, value):
    url = f'http://{host}:{port}/{path}'

    span = tracer.active_span
    span.set_tag(tags.HTTP_METHOD, 'GET')
    span.set_tag(tags.HTTP_URL, url)
    span.set_tag(tags.SPAN_KIND, tags.SPAN_KIND_RPC_CLIENT)
    headers = {}
    tracer.inject(span, Format.HTTP_HEADERS, headers)

    r = requests.get(url, params={param: value}, headers=headers)
    # assert r.status_code == 200, f"Real status_code: {r.status_code}"
    return r.text


@ns.route("/opentracing")
class Opentracing(Resource):
    @api.marshal_list_with(listed_todo)
    def get(self):
        """List all todos"""
        keys = list(TODOS.keys())
        say_hello_opentracing(host, TODOS[keys[0]]["task"])
        return [{"id": id, "todo": todo} for id, todo in TODOS.items()]


@ns.route("/ProcessHTTPRequestOpenTracing")
class ProcessHTTPRequestOpenTracing(Resource):
    def get(self):
        """
        Переслать get-запрос ProcessHTTPRequestOpenTracing на services_info (localhost:40100/ProcessHTTPRequestOpenTracing)
        """
        span_ctx = tracer.extract(Format.HTTP_HEADERS, request.headers)
        span_tags = {tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER}
        # resp = None
        with tracer.start_active_span('ProcessHTTPRequestOpenTracing', child_of=span_ctx, tags=span_tags):
            resp = http_get_opentracing(host, port, "ProcessHTTPRequestOpenTracing", "param1", "value1")

        return json.loads(resp)


@ns.route("/ProcessHTTPRequest")
class ProcessHTTPRequest(Resource):
    def get(self):
        """
        Переслать get-запрос ProcessHTTPRequestOpenTracing на services_info (localhost:40100/ProcessHTTPRequestOpenTracing)
        """
        span_ctx = tracer.extract(Format.HTTP_HEADERS, request.headers)
        span_tags = {tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER}
        resp = None
        with tracer.start_active_span('ProcessHTTPRequest', child_of=span_ctx, tags=span_tags):
            resp = http_get_opentracing(host, port, "ProcessHTTPRequest", "param1", "value1")

        return json.loads(resp)


@ns.route("/opentracing_log")
class Opentracing_log(Resource):
    @api.marshal_list_with(listed_todo)
    def get(self):
        """List all todos"""
        logging.getLogger("").debug(f"Opentracing_log 1")
        with tracer.start_span('TestSpan') as span:
            logging.getLogger("").debug(f"Opentracing_log 2")
            span.log_kv({'event': 'test message', 'life': 42})

            with tracer.start_span('ChildSpan', child_of=span) as child_span:
                logging.getLogger("").debug(f"Opentracing_log 3")
                span.log_kv({'event': 'up below'})
                child_span.log_kv({'event': 'down below'})
        return [{"id": id, "todo": todo} for id, todo in TODOS.items()]


@ns.route("/publish")
class Publish(Resource):
    @api.marshal_list_with(listed_todo)
    def get(self):
        """List all todos"""
        span_ctx = tracer.extract(Format.HTTP_HEADERS, request.headers)
        span_tags = {tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER}
        with tracer.start_active_span('publish', child_of=span_ctx, tags=span_tags):
            hello_str = request.args.get('helloStr')
            print(hello_str)
        return [{"id": id, "todo": todo} for id, todo in TODOS.items()]

    @api.doc(parser=parser)
    @api.marshal_with(todo, code=201)
    def post(self):
        """Create a todo"""
        args = parser.parse_args()
        todo_id = "todo%d" % (len(TODOS) + 1)
        TODOS[todo_id] = {"task": args["task"]}
        return TODOS[todo_id], 201


if __name__ == "__main__":
    app = Flask(__name__)
    app.register_blueprint(api_v1)
    app.run(port=30100, debug=True)



