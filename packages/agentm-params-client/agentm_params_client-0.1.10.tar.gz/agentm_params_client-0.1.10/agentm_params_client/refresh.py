import json, os, threading, time
from .client import ParamsClient

class ParamsRefresher:
    def __init__(self, base="http://localhost:8099", out_path="/tmp/params.cache.json", interval_s=15):
        self.base = base
        self.out_path = out_path
        self.interval_s = int(interval_s)
        self._stop = threading.Event()
        self._thr = None
        self._client = ParamsClient(base=self.base, cache_file=self.out_path + ".etag")

    def _write_atomic(self, data: dict):
        os.makedirs(os.path.dirname(self.out_path), exist_ok=True)
        tmp = self.out_path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(data, f)
        os.replace(tmp, self.out_path)

    def run(self):
        while not self._stop.is_set():
            try:
                params = self._client.fetch()
                if params:
                    self._write_atomic(params)
            except Exception:
                pass
            self._stop.wait(self.interval_s)

    def start(self):
        if self._thr and self._thr.is_alive():
            return
        self._thr = threading.Thread(target=self.run, daemon=True)
        self._thr.start()

    def stop(self):
        self._stop.set()

    def join(self, timeout=None):
        if self._thr:
            self._thr.join(timeout)
