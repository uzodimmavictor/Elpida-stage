import threading
from datetime import datetime, timedelta, timezone

from database.postgres import PostgresDB


class SuggestionService:
    """Return fresh Redis data or generate and cache a new pipeline result."""

    _REFRESHING = set()
    _REFRESHING_LOCK = threading.Lock()

    def __init__(self, agent, redis_db, ttl_seconds=900):
        self.agent = agent
        self.redis = redis_db
        self.ttl_seconds = int(ttl_seconds)
        self.cache_key = f"suggestions:{agent.nom}"

    def get_suggestions(self, force_refresh=False):
        cached = None if force_refresh else self.redis.get_json(self.cache_key)
        if cached and self._is_fresh(cached):
            result = dict(cached)
            result["source"] = "redis"
            return result
        return self.refresh()

    def get_or_trigger(self, ttl_seconds=None):
        ttl = ttl_seconds or self.ttl_seconds
        cached = self.redis.get_json(self.cache_key)

        if cached:
            generated_at = datetime.fromisoformat(cached["generated_at"])
            age = (datetime.now(timezone.utc) - generated_at).total_seconds()
            if age < ttl:
                return {**cached, "source": "redis"}

        result = {**(cached or {"suggestions": [], "generated_at": None}),
                  "source": "stale_cache"}

        with self._REFRESHING_LOCK:
            if self.cache_key not in self._REFRESHING:
                self._REFRESHING.add(self.cache_key)
                threading.Thread(target=self._background_refresh, daemon=True).start()

        return result

    def _background_refresh(self):
        try:
            self.refresh()
        except Exception as e:
            print(f"[SuggestionService] Background refresh failed: {e}")
        finally:
            with self._REFRESHING_LOCK:
                self._REFRESHING.discard(self.cache_key)

    def refresh(self):
        db = self.agent.getDependency("dbPostgres", PostgresDB)
        suggestions = self.agent.build_sales_suggestions(db)
        now = datetime.now(timezone.utc)
        document = {
            "agent": self.agent.nom,
            "suggestions": suggestions,
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
