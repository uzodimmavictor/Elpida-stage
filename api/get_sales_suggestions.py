from urllib.parse import parse_qs, urlparse

from api.rest_handler import RestHandler, Pair
from agent.sales import AgentSales


class GetSalesSuggestions(RestHandler):
    def process_request(self, request) -> Pair:
        params = parse_qs(urlparse(request.path).query)
        code = params.get("enseigne_id", [None])[0]
        ttl_seconds = request.server.rest_api.ttl_seconds
        agent = request.server.rest_api.getDependency("agentSales", AgentSales)
        result = agent.get_suggestions(code_etablissement=code, ttl_seconds=ttl_seconds)
        return Pair(result, 200)
