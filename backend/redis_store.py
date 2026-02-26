import json
from types import SimpleNamespace
from urllib.parse import urlparse
import redis


class RedisStore:
    """A minimal Redis-backed store compatible with the engine's get/put usage.

    API:
      get(namespace, key) -> SimpleNamespace(value=dict) or None
      put(namespace, key, value: dict)
    Namespace is a tuple (ns1, ns2) — we join them to form a redis key prefix.
    """

    def __init__(self, url: str):
        self.url = url
        parsed = urlparse(url)
        # Let redis.from_url handle the details
        self.client = redis.from_url(url, decode_responses=True)

    def _make_key(self, namespace, key):
        if isinstance(namespace, (list, tuple)):
            ns = ":".join(map(str, namespace))
        else:
            ns = str(namespace)
        return f"lg:{ns}:{key}"

    def get(self, namespace, key):
        rkey = self._make_key(namespace, key)
        raw = self.client.get(rkey)
        if raw is None:
            return None
        try:
            value = json.loads(raw)
        except Exception:
            value = {key: raw}
        return SimpleNamespace(value=value)

    def put(self, namespace, key, value: dict):
        rkey = self._make_key(namespace, key)
        self.client.set(rkey, json.dumps(value))
