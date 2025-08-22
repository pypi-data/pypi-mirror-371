import os, json, urllib.request

def _get(path):
    base = os.getenv("AGENTM_PARAMS_BASE_URL", "http://localhost:8099")
    with urllib.request.urlopen(base + path, timeout=5) as r:
        return r.status, dict(r.headers), r.read()

def test_hash():
    st, hdrs, body = _get('/v1/params/hash')
    assert st == 200
    j = json.loads(body.decode())
    assert isinstance(j.get('sha256'), str)

def test_head_headers():
    base = os.getenv("AGENTM_PARAMS_BASE_URL", "http://localhost:8099")
    req = urllib.request.Request(base + '/v1/params', method='HEAD')
    with urllib.request.urlopen(req, timeout=5) as r:
        hdrs = dict(r.headers)
    assert ('ETag' in hdrs) or ('X-Content-SHA256' in hdrs)
