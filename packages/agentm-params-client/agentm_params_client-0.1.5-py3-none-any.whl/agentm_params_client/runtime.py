import os, json
from .client import ParamsClient

def _load_cache(path: str):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return None

def load_params(base: str = None, cache_path: str = None):
    base = base or os.getenv("PARAMS_BASE", "http://params:8099")
    cache_path = cache_path or os.getenv("PARAMS_CACHE", "/data/params.cache.json")
    data = _load_cache(cache_path)
    if data:
        return data
    try:
        return ParamsClient(base=base, cache_file=(cache_path + ".etag")).fetch()
    except Exception:
        return {}

def params_snapshot():
    p = load_params()
    if not isinstance(p, dict):
        return {}
    snap = {
        "snapshot_version": (((p.get("signing") or {}).get("snapshot_version")) or "unknown"),
        "rate_limit": (p.get("rate_limit") or {}),
        "economics": (p.get("economics") or {}),
    }
    return snap
