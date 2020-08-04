from clients.http import Method


class Parse(Method):
    url = "parser/"
    m_type = "FILE"
    auth = None

    def __init__(self, files=""):
        Method.__init__(self)
        self.files = files


class HealthCheck(Method):
    _method = ""
    m_type = "GET"
    auth = None

