import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

from api.get_sales_suggestions import GetSalesSuggestions
from api.rest_handler import RestHandler


class Handler(BaseHTTPRequestHandler):
    handlers = {"GET": {"/suggestions/sales": GetSalesSuggestions()}}

    def do_GET(self):
        if not self.check_headers():
            self._send({"error": "invalid_headers"}, 400)
            return
        parsed = urlparse(self.path)
        handler = self.match_handler("GET", parsed.path)
        if not handler:
            self._send({"error": "route_not_found"}, 404)
            return
        response = handler.process_request(self)
        self._send(response.first, response.second)

    def _send(self, body, status):
        encoded = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, *_args):
        return

    def match_handler(self, method, path) -> RestHandler:
        method_handlers = self.handlers.get(method)
        if not method_handlers:
            return None
        for route, handler in method_handlers.items():
            if path.startswith(route):
                return handler
        return None

    def check_headers(self):
        user_agent = self.headers.get("User-Agent", "")
        accept = self.headers.get("Accept", "")
        content_type = self.headers.get("Content-Type", "")
        return True
