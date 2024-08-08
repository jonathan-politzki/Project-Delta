import httpx
from bs4 import BeautifulSoup
import feedparser
from urllib.parse import urljoin
import asyncio
from typing import List, Dict
import pandas as pd
import csv
import os
import logging
from asyncio.log import logger
from datetime import datetime
import xml.etree.ElementTree as ET
import requests

MAX_POSTS = 10  # Maximum number of posts to scrape per author

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def scrape_url(username: str, platform: str) -> Dict[str, List[Dict[str, str]]]:
    if platform.lower() == 'medium':
        return await scrape_medium(username)
    elif platform.lower() == 'substack':
        return await scrape_substack(username)
    else:
        raise ValueError("Unsupported platform. Please choose 'medium' or 'substack'.")

async def scrape_medium(username: str) -> Dict[str, List[Dict[str, str]]]:
    rss_url = f'https://medium.com/feed/@{username}'
    
    async with httpx.AsyncClient() as client:
        response = await client.get(rss_url)
        feed = feedparser.parse(response.text)
    
    entries = []
    for post in feed.entries[:MAX_POSTS]:
        soup = BeautifulSoup(post.content[0].value, 'html.parser')
        cleaned_text = soup.get_text(separator=' ', strip=True)
        entries.append({
            'title': post.title,
            'url': post.link,
            'content': cleaned_text,
            'date': post.published
        })
    
    return {'posts': entries}

async def scrape_substack(username: str) -> Dict[str, List[Dict[str, str]]]:
    base_url = f"https://{username}.substack.com"
    
    # Try to fetch URLs from sitemap
    sitemap_url = f"{base_url}/sitemap.xml"
    response = requests.get(sitemap_url)
    
    if response.ok:
        root = ET.fromstring(response.content)
        urls = [element.text for element in root.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    else:
        # Fall back to feed.xml
        feed_url = f"{base_url}/feed"
        response = requests.get(feed_url)
        if response.ok:
            root = ET.fromstring(response.content)
            urls = [item.find('link').text for item in root.findall('.//item') if item.find('link') is not None]
        else:
            logger.error(f"Failed to fetch sitemap and feed for {username}")
            return {"posts": []}

    posts = []
    for url in urls[:10]:  # Limit to 10 posts
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            title = soup.select_one("h1.post-title").text.strip() if soup.select_one("h1.post-title") else "No title"
            content = soup.select_one("div.available-content").get_text(strip=True) if soup.select_one("div.available-content") else "No content"
            date = soup.select_one("time")['datetime'] if soup.select_one("time") else "No date"
            
            posts.append({
                "title": title,
                "url": url,
                "content": content,
                "date": date
            })
        except Exception as e:
            logger.error(f"Error scraping post {url}: {str(e)}")

    return {"posts": posts}

def save_to_csv(data: Dict[str, List[Dict[str, str]]], filename: str):
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    full_filename = f"{filename}_{timestamp}.csv"
    filepath = os.path.join(output_dir, full_filename)
    
    if not data['posts']:
        logger.warning(f"No posts to save for {filename}")
        return None
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['title', 'url', 'content', 'date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for post in data['posts']:
            writer.writerow(post)
    
    logger.info(f"Saved {len(data['posts'])} posts to {filepath}")
    return filepath

# Helper function to convert scraper output to DataFrame
def scraper_output_to_df(data: Dict[str, List[Dict[str, str]]]) -> pd.DataFrame:
    return pd.DataFrame(data['posts'])