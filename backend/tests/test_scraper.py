# backend/tests/test_scraper.py

import pytest
from scraper import scrape_url, save_to_csv
import os
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_scrape_medium_with_csv():
    username = "travismay"
    result = await scrape_url(username, 'medium')
    assert isinstance(result, dict)
    assert "posts" in result
    assert len(result["posts"]) <= 10  # Check MAX_POSTS limit
    
    # Save to CSV
    csv_path = save_to_csv(result, f"{username}_medium")
    assert os.path.exists(csv_path)
    
    # Check CSV content
    df = pd.read_csv(csv_path)
    assert not df.empty
    assert all(column in df.columns for column in ['title', 'url', 'content', 'date', 'subtitle', 'like_count'])

@pytest.mark.asyncio
async def test_scrape_substack_with_csv():
    username = "jonathanpolitzki"
    result = await scrape_url(username, 'substack')
    assert isinstance(result, dict)
    assert "posts" in result
    
    if not result["posts"]:
        logger.warning(f"No posts found for Substack user: {username}")
        return
    
    assert len(result["posts"]) <= 10  # Check MAX_POSTS limit
    
    # Save to CSV
    csv_path = save_to_csv(result, f"{username}_substack")
    if csv_path:
        assert os.path.exists(csv_path)
        
        # Check CSV content
        df = pd.read_csv(csv_path)
        assert not df.empty
        assert all(column in df.columns for column in ['title', 'subtitle', 'url', 'content', 'date', 'like_count'])
    else:
        logger.warning("No CSV file was generated due to lack of data")

@pytest.mark.asyncio
async def test_unsupported_platform():
    with pytest.raises(ValueError):
        await scrape_url("username", "unsupported_platform")