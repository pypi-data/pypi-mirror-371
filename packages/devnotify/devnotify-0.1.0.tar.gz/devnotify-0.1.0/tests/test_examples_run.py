# tests/test_examples_run.py
import json
import pathlib
import runpy

import pytest

EXAMPLES_DIR = pathlib.Path(__file__).parent.parent / "examples"


class DummyResponse:
    def __init__(self):
        self.status_code = 200
        self.text = "ok"

    def json(self):
        return {"status": "ok"}


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    # Provide fake config so examples don't need real creds/servers
    monkeypatch.setenv("DEVNOTIFY_API_KEY", "devk_test")
    # Use any placeholder; we mock network anyway
    monkeypatch.setenv("DEVNOTIFY_BASE_URL", "http://dev-host")


@pytest.fixture(autouse=True)
def _mock_requests(monkeypatch):
    import requests

    def fake_post(url, headers=None, data=None, timeout=None):
        # smoke-check that payload is valid JSON
        if data:
            json.loads(data)
        return DummyResponse()

    monkeypatch.setattr(requests, "post", fake_post)


@pytest.mark.parametrize("example", sorted(EXAMPLES_DIR.glob("*.py")))
def test_example_runs(example):
    runpy.run_path(str(example), run_name="__main__")
