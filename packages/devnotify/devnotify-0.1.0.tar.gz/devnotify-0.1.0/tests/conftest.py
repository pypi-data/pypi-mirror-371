import pytest

import devnotify


@pytest.fixture(autouse=True)
def reset_env_and_globals(monkeypatch):
    # Clear global api key
    devnotify.api_key = None
    # Clear env
    monkeypatch.delenv("DEVNOTIFY_API_KEY", raising=False)
    monkeypatch.delenv("DEVNOTIFY_BASE_URL", raising=False)
    yield
    # Clean up
    devnotify.api_key = None


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    # avoid delays during retry tests
    monkeypatch.setattr("time.sleep", lambda *_a, **_k: None)
