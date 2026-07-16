import json
import threading
from http.server import  ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
from api.handler import Handler
from agent.sales.sales import AgentSales
from agent.suggestion_service import SuggestionService
from component.component import Component
from component.component_registry import registry
from component.dependency import Dependency
from database.redis import RedisDB


@registry("RestAPI")
class RestAPI(Component):
    dependencies = [Dependency("agentSales", AgentSales), Dependency("redis", RedisDB)]
   

    def __init__(self, nom, isConfigurable):
        super().__init__(nom, isConfigurable)
        self.host = "0.0.0.0"
        self.port = 8080
        self.api_key = None
        self.ttl_seconds = 900
        self.server = None
        self.thread = None
    
 
    def configure(self, config_data):
        self.host = config_data.get("host", self.host)
        self.port = int(config_data.get("port", self.port))
        self.api_key = config_data.get("api_key")
        self.ttl_seconds = int(config_data.get("ttl_seconds", self.ttl_seconds))

    def isConfigured(self):
        return bool(self.host and self.port > 0 and self.ttl_seconds > 0)

    def onEnterLoop(self):
        agent = self.getDependency("agentSales", AgentSales)
        redis_db = self.getDependency("redis", RedisDB)
        service = SuggestionService(agent, redis_db, self.ttl_seconds)
        agent.suggestion_service = service
        expected_agent = agent.nom
        api_key = self.api_key


       
        self.server = ThreadingHTTPServer((self.host, self.port), Handler)
        self.server.rest_api = self
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        print(f"[{self.nom}] REST API listening on http://{self.host}:{self.port}")
        return True

    def disconnect(self):
        if self.server is not None:
            self.server.shutdown()
            self.server.server_close()
            self.server = None
        if self.thread is not None:
            self.thread.join(timeout=2)
            self.thread = None
