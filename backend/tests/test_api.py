# backend/tests/test_api.py

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_analyze_medium_url():
    response = client.post("/api/v1/analysis/", json={"url": "https://medium.com/@travismay"})
    if response.status_code != 200:
        print(f"Error response: {response.json()}")
    assert response.status_code == 200
    data = response.json()
    assert "insights" in data
    assert "writing_style" in data
    assert "key_themes" in data
    assert "readability_score" in data
    assert "sentiment" in data
    assert "post_count" in data

def test_analyze_substack_url():
    response = client.post("/api/v1/analysis/", json={"url": "https://jonathanpolitzki.substack.com/"})
    assert response.status_code == 200
    data = response.json()
    assert "insights" in data
    assert "writing_style" in data
    assert "key_themes" in data
    assert "readability_score" in data
    assert "sentiment" in data
    assert "post_count" in data


def test_invalid_url():
    response = client.post("/api/v1/analysis/", json={"url": "https://invalid-url.com"})
    assert response.status_code == 400