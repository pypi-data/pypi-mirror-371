import os
import pytest

os.environ["API_KEYS"] = "testkey"

pytest.importorskip("transformers")

import server
from fastapi.testclient import TestClient


HEADERS = {"Authorization": "Bearer testkey"}


def make_client(monkeypatch):
    def dummy_load_model():
        server.model_manager.tokenizer = object()
        server.model_manager.model = object()
    monkeypatch.setattr(server.model_manager, "load_model", dummy_load_model)
    return TestClient(server.app)


def test_chat_completions_validation(monkeypatch):
    with make_client(monkeypatch) as client:
        resp = client.post(
            "/v1/chat/completions",
            json={"messages": [{"role": "user", "content": "hi"}], "temperature": 2.1},
            headers=HEADERS,
        )
        assert resp.status_code == 422

        resp = client.post(
            "/v1/chat/completions",
            json={"messages": [{"role": "user", "content": "hi"}], "max_tokens": 513},
            headers=HEADERS,
        )
        assert resp.status_code == 422


def test_completions_validation(monkeypatch):
    with make_client(monkeypatch) as client:
        resp = client.post(
            "/v1/completions",
            json={"prompt": "hi", "temperature": -0.1},
            headers=HEADERS,
        )
        assert resp.status_code == 422

        resp = client.post(
            "/v1/completions",
            json={"prompt": "hi", "max_tokens": 0},
            headers=HEADERS,
        )
        assert resp.status_code == 422
