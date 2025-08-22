import devnotify
from devnotify import AuthError, DevNotify, NetworkError, RateLimitError, ServerError


class R:
    def __init__(self, code=200, payload=None, text=""):
        self.status_code = code
        self._payload = payload
        self.text = text
        devnotify.api_key = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
            "eyJzdWIiOiIxYWMyNDZkYS0xM2U3LTQyNTQtOWM4NS00YTVhNjg0YWJlYmEiLCJleHAiOjE3NTU0MTU0OTJ9."
            "c0B7msrK0BuPbtCA5zI1ox0Og4nL9vd_WDnqEbh0KVc"
        )

    def json(self):
        if self._payload is None:
            raise ValueError("no json")
        return self._payload


def test_success(monkeypatch):
    def fake_post(*a, **k):
        return R(200, {"status": "ok", "id": "n1"})

    import requests

    monkeypatch.setattr(requests, "post", fake_post)
    c = DevNotify("k")
    assert c.send("hi")["status"] == "ok"


def test_401(monkeypatch):
    def fake_post(*a, **k):
        return R(401, text="bad key")

    import requests

    monkeypatch.setattr(requests, "post", fake_post)
    c = DevNotify("k")
    try:
        c.send("hi")
        assert AssertionError()
    except AuthError:
        assert True


def test_429(monkeypatch):
    def fake_post(*a, **k):
        return R(429, text="limit")

    import requests

    monkeypatch.setattr(requests, "post", fake_post)
    c = DevNotify("k")
    try:
        c.send("hi")
        assert AssertionError()
    except RateLimitError:
        assert True


def test_5xx_retry_then_fail(monkeypatch):
    calls = {"n": 0}

    def fake_post(*a, **k):
        calls["n"] += 1
        return R(500, text="boom")

    import requests

    monkeypatch.setattr(requests, "post", fake_post)
    c = DevNotify("k", retries=1, backoff=0)
    try:
        c.send("hi")
        assert AssertionError()
    except ServerError:
        assert calls["n"] >= 2


def test_network(monkeypatch):
    class E(Exception):
        pass

    def fake_post(*a, **k):
        import requests

        raise requests.ConnectionError("no route")

    import requests

    monkeypatch.setattr(requests, "post", fake_post)
    c = DevNotify("k", retries=0)
    try:
        c.send("hi")
        raise AssertionError()
    except NetworkError:
        assert True
