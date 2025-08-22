import json

import pytest

import devnotify
from devnotify import DevNotify
from devnotify.exceptions import (
    AuthError,
    DevNotifyError,
    NetworkError,
    RateLimitError,
    ServerError,
)


class DummyResponse:
    def __init__(self, status_code=200, payload=None, text="ok"):
        self.status_code = status_code
        self._payload = payload
        self.text = text

    def json(self):
        if self._payload is None:
            raise ValueError("no json")
        return self._payload


def patch_post(monkeypatch, fn):
    import requests

    monkeypatch.setattr(requests, "post", fn)


def capture_post(monkeypatch, status_code=200, payload=None, text="ok"):
    calls = {"n": 0, "headers": None, "data": None, "url": None}

    def fake_post(url, headers=None, data=None, timeout=None):
        calls["n"] += 1
        calls["headers"] = headers
        calls["data"] = json.loads(data) if data else None
        calls["url"] = url
        return DummyResponse(status_code, payload, text)

    patch_post(monkeypatch, fake_post)
    return calls


def test_success_json(monkeypatch):
    devnotify.api_key = "k1"
    calls = capture_post(monkeypatch, 200, {"status": "ok", "id": "n1"})
    monkeypatch.setenv("DEVNOTIFY_BASE_URL", "http://local")
    out = DevNotify().send(
        "hello", title="t", tags=["a", "b"], priority="normal", silent=True
    )
    assert out["status"] == "ok"
    assert calls["headers"]["Authorization"] == "Bearer k1"
    assert calls["headers"]["Accept"] == "application/json"
    assert calls["headers"]["Content-Type"] == "application/json"
    assert calls["url"] == "http://local/notification/create"
    assert calls["data"]["message"] == "hello"
    assert calls["data"]["title"] == "t"
    assert calls["data"]["priority"] == "normal"
    assert calls["data"]["tags"] == ["a", "b"]
    assert calls["data"]["silent"] is True


def test_success_non_json(monkeypatch):
    devnotify.api_key = "k1"
    calls = capture_post(monkeypatch, 200, payload=None, text="ok-text")
    monkeypatch.setenv("DEVNOTIFY_BASE_URL", "http://local")
    out = DevNotify().send("hi")
    assert out["status"] == "ok"
    assert out["raw"] == "ok-text"
    assert calls["n"] == 1


def test_401_raises_auth(monkeypatch):
    devnotify.api_key = "k"
    calls = capture_post(monkeypatch, 401, payload=None, text="bad key")
    monkeypatch.setenv("DEVNOTIFY_BASE_URL", "http://local")
    with pytest.raises(AuthError):
        DevNotify().send("hello")
    assert calls["n"] == 1


def test_429_raises_rate_limit(monkeypatch):
    devnotify.api_key = "k"
    calls = capture_post(monkeypatch, 429, payload=None, text="limit")
    monkeypatch.setenv("DEVNOTIFY_BASE_URL", "http://local")
    with pytest.raises(RateLimitError):
        DevNotify().send("hello")
    assert calls["n"] == 1


def test_other_4xx_raises_generic(monkeypatch):
    devnotify.api_key = "k"
    calls = capture_post(monkeypatch, 404, payload=None, text="nope")
    monkeypatch.setenv("DEVNOTIFY_BASE_URL", "http://local")
    with pytest.raises(DevNotifyError) as e:
        DevNotify().send("hello")
    assert "404" in str(e.value)
    assert calls["n"] == 1


def test_5xx_retries_then_success(monkeypatch):
    devnotify.api_key = "k"
    seq = iter([DummyResponse(500, text="boom"), DummyResponse(200, {"status": "ok"})])

    def fake_post(url, headers=None, data=None, timeout=None):
        return next(seq)

    patch_post(monkeypatch, fake_post)
    monkeypatch.setenv("DEVNOTIFY_BASE_URL", "http://local")
    out = DevNotify(retries=1, backoff=0).send("hello")
    assert out["status"] == "ok"


def test_5xx_exhaust_retries(monkeypatch):
    devnotify.api_key = "k"

    # always 500
    def fake_post(url, headers=None, data=None, timeout=None):
        return DummyResponse(500, text="boom")

    patch_post(monkeypatch, fake_post)
    monkeypatch.setenv("DEVNOTIFY_BASE_URL", "http://local")
    with pytest.raises(ServerError):
        DevNotify(retries=1, backoff=0).send("hello")


def test_network_error_retry_then_fail(monkeypatch):
    devnotify.api_key = "k"
    import requests

    calls = {"n": 0}

    def fake_post(url, headers=None, data=None, timeout=None):
        calls["n"] += 1
        raise requests.ConnectionError("no route")

    patch_post(monkeypatch, fake_post)
    monkeypatch.setenv("DEVNOTIFY_BASE_URL", "http://local")
    with pytest.raises(NetworkError):
        DevNotify(retries=1, backoff=0).send("hello")
    assert calls["n"] >= 2  # initial + retry


def test_network_error_retry_then_success(monkeypatch):
    devnotify.api_key = "k"
    import requests

    seq = iter([("err", None), ("ok", DummyResponse(200, {"status": "ok"}))])

    def fake_post(url, headers=None, data=None, timeout=None):
        tag, resp = next(seq)
        if tag == "err":
            raise requests.Timeout("slow")
        return resp

    patch_post(monkeypatch, fake_post)
    monkeypatch.setenv("DEVNOTIFY_BASE_URL", "http://local")
    out = DevNotify(retries=2, backoff=0).send("hello")
    assert out["status"] == "ok"


def test_env_base_url_used(monkeypatch):
    devnotify.api_key = "k"
    calls = capture_post(monkeypatch, 200, {"status": "ok"})
    monkeypatch.setenv("DEVNOTIFY_BASE_URL", "http://devhost:9000")
    DevNotify().send("x")
    assert calls["url"] == "http://devhost:9000/notification/create"


def test_input_validation(monkeypatch):
    devnotify.api_key = "k"
    monkeypatch.setenv("DEVNOTIFY_BASE_URL", "http://local")

    # empty message
    with pytest.raises(ValueError):
        DevNotify().send("")

    # bad priority
    with pytest.raises(ValueError):
        DevNotify().send("ok", priority="urgent")
