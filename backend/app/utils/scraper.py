# backend/app/utils/scraper.py

import httpx
from bs4 import BeautifulSoup
import feedparser
from urllib.parse import urljoin, urlparse, urlparse, urlunparse
import asyncio
from typing import List, Dict, Optional
import pandas as pd
import csv
import os
import logging
import xml.etree.ElementTree as ET
import requests
from datetime import datetime
from tqdm import tqdm
import json
import re

MAX_POSTS = 10
BASE_DIR_NAME = "output"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_main_part(url: str) -> str:
    parts = urlparse(url).netloc.split('.')
    return parts[1] if parts[0] == 'www' else parts[0]

def clean_content(content: str) -> str:
    # Remove extra whitespace and newlines
    content = re.sub(r'\s+', ' ', content).strip()
    # Escape double quotes
    content = content.replace('"', '""')
    return content

class BaseSubstackScraper:
    def __init__(self, base_substack_url: str, save_dir: str):
        if not base_substack_url.endswith("/"):
            base_substack_url += "/"
        self.base_substack_url: str = base_substack_url
        self.writer_name: str = extract_main_part(base_substack_url)
        self.save_dir: str = save_dir
        os.makedirs(self.save_dir, exist_ok=True)
        self.keywords: List[str] = ["about", "archive", "podcast"]
        self.post_urls: List[str] = self.get_all_post_urls()

    def get_all_post_urls(self) -> List[str]:
        urls = self.fetch_urls_from_sitemap()
        if not urls:
            urls = self.fetch_urls_from_feed()
        return self.filter_urls(urls, self.keywords)

    def fetch_urls_from_sitemap(self) -> List[str]:
        sitemap_url = f"{self.base_substack_url}sitemap.xml"
        response = requests.get(sitemap_url)
        if not response.ok:
            logger.error(f'Error fetching sitemap at {sitemap_url}: {response.status_code}')
            return []
        root = ET.fromstring(response.content)
        return [element.text for element in root.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]

    def fetch_urls_from_feed(self) -> List[str]:
        logger.info('Falling back to feed.xml. This will only contain up to the 22 most recent posts.')
        feed_url = f"{self.base_substack_url}feed"
        response = requests.get(feed_url)
        if not response.ok:
            logger.error(f'Error fetching feed at {feed_url}: {response.status_code}')
            return []
        root = ET.fromstring(response.content)
        return [item.find('link').text for item in root.findall('.//item') if item.find('link') is not None]

    @staticmethod
    def filter_urls(urls: List[str], keywords: List[str]) -> List[str]:
        return [url for url in urls if all(keyword not in url for keyword in keywords)]

    def get_url_soup(self, url: str) -> Optional[BeautifulSoup]:
        try:
            response = requests.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except Exception as e:
            logger.error(f"Error fetching page {url}: {str(e)}")
            return None

    def extract_post_data(self, soup: BeautifulSoup, url: str) -> Dict[str, str]:
        title = soup.select_one("h1.post-title, h2").text.strip() if soup.select_one("h1.post-title, h2") else "No title"
        subtitle_element = soup.select_one("h3.subtitle")
        subtitle = subtitle_element.text.strip() if subtitle_element else ""
        date_element = soup.select_one(".pencraft.pc-display-flex.pc-gap-4.pc-reset .pencraft")
        date = date_element.text.strip() if date_element else "Date not available"
        like_count_element = soup.select_one("a.post-ufi-button .label")
        like_count = like_count_element.text.strip() if like_count_element else "Like count not available"
        content_element = soup.select_one("div.available-content")
        content = content_element.get_text(separator=' ', strip=True) if content_element else "No content"
        content = clean_content(content)
        
        return {
            "title": clean_content(title),
            "subtitle": clean_content(subtitle),
            "url": url,
            "content": content,
            "date": clean_content(date),
            "like_count": clean_content(like_count)
        }

    def scrape_posts(self, num_posts_to_scrape: int = 0) -> List[Dict[str, str]]:
        posts_data = []
        total = min(num_posts_to_scrape, len(self.post_urls)) if num_posts_to_scrape != 0 else len(self.post_urls)
        for url in tqdm(self.post_urls[:total], total=total):
            try:
                soup = self.get_url_soup(url)
                if soup is None:
                    continue
                post_data = self.extract_post_data(soup, url)
                posts_data.append(post_data)
            except Exception as e:
                logger.error(f"Error scraping post: {e}")
        return posts_data

from urllib.parse import urlparse

async def scrape_medium(url: str) -> Dict[str, List[Dict[str, str]]]:
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip('/').split('/')
    
    if parsed_url.netloc == 'medium.com':
        username = path_parts[0] if path_parts else ''
    else:
        username = parsed_url.netloc.split('.')[0]
    
    if username.startswith('@'):
        username = username[1:]
    
    rss_url = f'https://medium.com/feed/@{username}'
    
    logger.info(f"Fetching RSS feed from: {rss_url}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(rss_url)
            response.raise_for_status()
            logger.info(f"RSS feed fetched successfully. Status code: {response.status_code}")
            feed = feedparser.parse(response.text)
            logger.info(f"Number of entries in feed: {len(feed.entries)}")
        except Exception as e:
            logger.error(f"Error fetching RSS feed: {str(e)}")
            return {'posts': []}

    entries = []
    for post in feed.entries[:MAX_POSTS]:
        try:
            soup = BeautifulSoup(post.content[0].value, 'html.parser')
            cleaned_text = clean_content(soup.get_text(separator=' ', strip=True))
            entries.append({
                'title': clean_content(post.title),
                'url': post.link,
                'content': cleaned_text,
                'date': clean_content(post.published),
                'subtitle': '',
                'like_count': 'N/A'
            })
        except Exception as e:
            logger.error(f"Error processing post {post.link}: {str(e)}")

    logger.info(f"Scraped {len(entries)} posts from Medium")
    return {'posts': entries}

async def scrape_substack(url: str) -> Dict[str, List[Dict[str, str]]]:
    parsed_url = urlparse(url)
    
    # Ensure the scheme (protocol) is set
    if not parsed_url.scheme:
        parsed_url = parsed_url._replace(scheme='https')
    
    base_url = urlunparse(parsed_url)
    
    logger.info(f"Fetching Substack posts from: {base_url}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{base_url}/feed")
            response.raise_for_status()
            feed = feedparser.parse(response.text)
            logger.info(f"Number of entries in feed: {len(feed.entries)}")
        except Exception as e:
            logger.error(f"Error fetching Substack feed: {str(e)}")
            return {'posts': []}

    entries = []
    for post in feed.entries[:MAX_POSTS]:
        try:
            content = post.content[0].value if 'content' in post else post.summary
            soup = BeautifulSoup(content, 'html.parser')
            cleaned_text = clean_content(soup.get_text(separator=' ', strip=True))
            entries.append({
                'title': clean_content(post.title),
                'url': post.link,
                'content': cleaned_text,
                'date': clean_content(post.published),
                'subtitle': '',
                'like_count': 'N/A'
            })
        except Exception as e:
            logger.error(f"Error processing Substack post {post.link}: {str(e)}")

    logger.info(f"Scraped {len(entries)} posts from Substack")
    return {'posts': entries}

async def scrape_url(url: str) -> Dict[str, List[Dict[str, str]]]:
    try:
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError(f"Invalid URL format: {url}")
        
        if 'medium.com' in parsed_url.netloc:
            return await scrape_medium(url)
        elif 'substack.com' in parsed_url.netloc:
            return await scrape_substack(url)
        else:
            raise ValueError(f"Unsupported URL: {url}")
    except Exception as e:
        logger.error(f"Error scraping URL {url}: {str(e)}")
        raise

def save_to_csv(data: Dict[str, List[Dict[str, str]]], filename: str):
    os.makedirs(BASE_DIR_NAME, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    full_filename = f"{filename}_{timestamp}.csv"
    filepath = os.path.join(BASE_DIR_NAME, full_filename)
    if not data['posts']:
        logger.warning(f"No posts to save for {filename}")
        return None
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['title', 'subtitle', 'url', 'content', 'date', 'like_count']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for post in data['posts']:
            writer.writerow(post)
    logger.info(f"Saved {len(data['posts'])} posts to {filepath}")
    return filepath

def scraper_output_to_df(data: Dict[str, List[Dict[str, str]]]) -> pd.DataFrame:
    return pd.DataFrame(data['posts'])