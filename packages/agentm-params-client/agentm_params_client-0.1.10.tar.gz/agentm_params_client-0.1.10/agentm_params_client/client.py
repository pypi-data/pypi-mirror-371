import json, os, urllib.request, urllib.error

class ParamsClient:
    def __init__(self, base=None, base_url=None, cache_file="/tmp/agentm_params_cache.json"):
        import os
        if base is None:
            base = base_url or os.getenv("AGENTM_PARAMS_BASE_URL","http://localhost:8099")
        self.base = base.rstrip("/")
        self.cache_file = cache_file

        self.base = base.rstrip("/")
        self.cache_file = cache_file

    def _load_cache(self):
        if not os.path.exists(self.cache_file):
            return {}
        try:
            with open(self.cache_file, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_cache(self, data):
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        with open(self.cache_file, "w") as f:
            json.dump(data, f)

    def fetch(self):
        cache = self._load_cache()
        headers = {}
        etag = cache.get("etag")
        if etag:
            headers["If-None-Match"] = etag

        req = urllib.request.Request(self.base + "/v1/params", headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                if r.status == 304:
                    return cache.get("params")
                body = r.read().decode()
                params = json.loads(body)
                etag = r.headers.get("ETag")
                sha = r.headers.get("X-Content-SHA256")
                cache.update({"params": params, "etag": etag, "sha256": sha})
                self._save_cache(cache)
                return params
        except urllib.error.HTTPError as e:
            if e.code == 304:
                return cache.get("params")
            raise


def _agentm__ensure_methods():
    import json, urllib.request, os
    cls = ParamsClient
    if not hasattr(cls, "_http"):
        def _http(self, method, path, data=None, headers=None):
            u = self.base + path
            h = {} if headers is None else dict(headers)
            body = None
            if data is not None:
                body = json.dumps(data).encode("utf-8")
                h["Content-Type"] = "application/json"
            r = urllib.request.Request(u, method=method, data=body, headers=h)
            with urllib.request.urlopen(r, timeout=10) as resp:
                return resp.status, dict(resp.headers), resp.read()
        setattr(cls, "_http", _http)

    if not hasattr(cls, "health"):
        def health(self):
            st, _, _ = self._http("GET", "/health")
            return st == 200
        setattr(cls, "health", health)

    if not hasattr(cls, "get_params"):
        def get_params(self):
            st, _, body = self._http("GET", "/v1/params")
            if st != 200:
                raise RuntimeError(f"unexpected status: {st}")
            return json.loads(body.decode())
        setattr(cls, "get_params", get_params)

    if not hasattr(cls, "get_hash"):
        def get_hash(self):
            st, _, body = self._http("GET", "/v1/params/hash")
            if st != 200:
                raise RuntimeError(f"unexpected status: {st}")
            return json.loads(body.decode()).get("sha256")
        setattr(cls, "get_hash", get_hash)

    if not hasattr(cls, "apply"):
        def apply(self, proposal: dict, signatures: list[dict], admin_token: str | None = None):
            tok = admin_token or os.getenv("AGENTM_PARAMS_ADMIN_TOKEN")
            hdr = {"x-admin-token": tok} if tok else {}
            payload = {"proposal": proposal, "signatures": signatures}
            st, _, body = self._http("POST", "/v1/params/apply", data=payload, headers=hdr)
            if st != 200:
                try:
                    detail = json.loads(body.decode())
                except Exception:
                    detail = body.decode(errors="ignore")
                raise RuntimeError(f"apply failed: status {st}; detail: {detail}")
            return json.loads(body.decode())
    setattr(cls, "apply", apply)

_agentm__ensure_methods()
