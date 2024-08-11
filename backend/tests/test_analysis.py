import pytest
from fastapi.testclient import TestClient
from main import app
from app.services.text_processor import process_text
from app.services.embedding_service import generate_embedding
from app.services.analysis_service import generate_analysis
from openai.error import OpenAIError


client = TestClient(app)

def test_analyze_url():
    response = client.post("/api/v1/analysis/", json={"url": "https://medium.com/@travismay"})
    assert response.status_code in [200, 503]  # 503 if OpenAI API is unavailable
    if response.status_code == 200:
        data = response.json()
        assert "insights" in data
        assert "writing_style" in data
        assert "key_themes" in data
        assert "readability_score" in data
        assert "sentiment" in data
        assert "post_count" in data

def test_text_processing():
    sample_text = "This is a sample text for testing. It contains multiple sentences."
    processed = process_text(sample_text)
    assert 'processed_text' in processed
    assert 'sentence_count' in processed
    assert 'word_count' in processed


def test_embedding_generation():
    # This test might need to be adjusted or skipped if it directly calls OpenAI API
    pass

@pytest.mark.asyncio
async def test_analysis_generation():
    # This test might need to be adjusted or skipped if it directly calls OpenAI API
    pass

