import threading
from datetime import datetime, timedelta, timezone

from database.postgres import PostgresDB


class SuggestionService:
    """Return fresh Redis data or generate and cache a new pipeline result."""

    def __init__(self, agent, redis_db, ttl_seconds=900):
        self.agent = agent
        self.redis = redis_db
        self.ttl_seconds = int(ttl_seconds)
        self.cache_key = f"suggestions:{agent.nom}"
        self._lock = threading.Lock()

    def get_suggestions(self, force_refresh=False):
        cached = None if force_refresh else self.redis.get_json(self.cache_key)
        if cached and self._is_fresh(cached):
            result = dict(cached)
            result["source"] = "redis"
            return result

        with self._lock:
            cached = None if force_refresh else self.redis.get_json(self.cache_key)
            if cached and self._is_fresh(cached):
                result = dict(cached)
                result["source"] = "redis"
                return result
            return self.refresh()

    def refresh(self):
        db = self.agent.getDependency("dbPostgres", PostgresDB)
        suggestion = self.agent.build_sales_suggestion(db)
        now = datetime.now(timezone.utc)
        document = {
            "agent": self.agent.nom,
            "suggestions": [suggestion],
            "generated_at": now.isoformat(),
            "expires_at": (now + timedelta(seconds=self.ttl_seconds)).isoformat(),
        }
        # The same key is deliberately overwritten on every refresh.
        self.redis.set_json(self.cache_key, document, self.ttl_seconds)
        document["source"] = "pipeline"
        return document

    @staticmethod
    def _is_fresh(document):
        try:
            expires_at = datetime.fromisoformat(document["expires_at"])
            return datetime.now(timezone.utc) < expires_at
        except (KeyError, TypeError, ValueError):
            return False
