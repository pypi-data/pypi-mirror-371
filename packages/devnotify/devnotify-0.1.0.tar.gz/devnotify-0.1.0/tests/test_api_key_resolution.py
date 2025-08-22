import json

import pytest

import devnotify
from devnotify import DevNotify


class DummyResponse:
    def __init__(self, status_code=200, payload=None, text="ok"):
        self.status_code = status_code
        self._payload = payload if payload is not None else {"status": "ok"}
        self.text = text

    def json(self):
        return self._payload


def _patch_post(monkeypatch, capture):
    import requests

    def fake_post(url, headers=None, data=None, timeout=None):
        capture["url"] = url
        capture["headers"] = headers or {}
        capture["data"] = json.loads(data) if data else None
        return DummyResponse(200, {"status": "ok"})

    monkeypatch.setattr(requests, "post", fake_post)


def test_ctor_api_key_wins_over_global_and_env(monkeypatch):
    # Arrange
    capture = {}
    _patch_post(monkeypatch, capture)
    devnotify.api_key = "global_abc"
    monkeypatch.setenv("DEVNOTIFY_API_KEY", "env_abc")
    monkeypatch.setenv("DEVNOTIFY_BASE_URL", "http://local")

    # Act
    client = DevNotify(api_key="ctor_abc")
    client.send("hello")

    # Assert
    assert capture["headers"]["Authorization"] == "Bearer ctor_abc"


def test_global_used_when_no_ctor(monkeypatch):
    capture = {}
    _patch_post(monkeypatch, capture)
    devnotify.api_key = "global_abc"
    monkeypatch.setenv("DEVNOTIFY_API_KEY", "env_abc")
    monkeypatch.setenv("DEVNOTIFY_BASE_URL", "http://local")

    # Act
    client = DevNotify()
    client.send("hello")

    # Assert
    assert capture["headers"]["Authorization"] == "Bearer global_abc"


def test_env_used_when_no_ctor_and_no_global(monkeypatch):
    capture = {}
    _patch_post(monkeypatch, capture)
    # no ctor, no global
    monkeypatch.setenv("DEVNOTIFY_API_KEY", "env_abc")
    monkeypatch.setenv("DEVNOTIFY_BASE_URL", "http://local")

    # Act
    client = DevNotify()
    client.send("hello")

    # Assert
    assert capture["headers"]["Authorization"] == "Bearer env_abc"


def test_missing_key_raises(monkeypatch):
    # No ctor, no global, no env
    with pytest.raises(RuntimeError) as e:
        DevNotify()  # __post_init__ should raise via get_api_key()
    assert "devnotify api key missing" in str(e.value).lower()


def test_header_contains_key_on_send(monkeypatch):
    capture = {}
    _patch_post(monkeypatch, capture)
    devnotify.api_key = "global_abc"
    monkeypatch.setenv("DEVNOTIFY_BASE_URL", "http://local")

    client = DevNotify()

    client.send("msg", title="T", priority="normal", tags=["a", "b"], silent=True)

    assert capture["headers"]["Authorization"] == "Bearer global_abc"
    assert capture["data"]["message"] == "msg"
    assert capture["data"]["title"] == "T"
    assert capture["data"]["priority"] == "normal"
    assert capture["data"]["tags"] == ["a", "b"]
    assert capture["data"]["silent"] is True
