# Copyright The OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from sys import argv

from requests import get

from opentelemetry import propagators
from opentelemetry.fastapi.utils import get_param
from opentelemetry.fastapi.ot_utils import init_jaeger

jaeger_host, server1_port, server2_port = get_param()

tracer = init_jaeger(jaeger_host, 'fastapi_opentelemetry_client')

assert len(argv) == 2

with tracer.start_as_current_span("client"):

    with tracer.start_as_current_span("client-server"):
        headers = {}
        propagators.inject(dict.__setitem__, headers)
        requested = get(
            f"http://localhost:{server1_port}/server_request",
            params={"param": argv[1]},
            headers=headers,
        )

        assert requested.status_code == 200 or requested.status_code == 201
