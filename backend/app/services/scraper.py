import httpx
from bs4 import BeautifulSoup
import feedparser
from urllib.parse import urlparse, urljoin
import asyncio
from typing import List, Dict

MAX_POSTS = 10  # Maximum number of posts to scrape per author

async def scrape_url(url: str) -> Dict[str, List[Dict[str, str]]]:
    parsed_url = urlparse(url)
    domain = parsed_url.netloc

    if 'medium.com' in domain:
        return await scrape_medium(url)
    elif 'substack.com' in domain:
        return await scrape_substack(url)
    else:
        raise ValueError("Unsupported URL. Please provide a Medium or Substack URL.")

async def scrape_medium(url: str) -> Dict[str, List[Dict[str, str]]]:
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.split('/')
    username = path_parts[1] if len(path_parts) > 1 else None
    
    if not username:
        raise ValueError("Invalid Medium URL. Unable to extract username.")
    
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

async def scrape_substack(url: str) -> Dict[str, List[Dict[str, str]]]:
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    
    async with httpx.AsyncClient() as client:
        posts = []
        page = 1
        while len(posts) < MAX_POSTS:
            archive_url = f"{base_url}/archive?sort=new&page={page}"
            response = await client.get(archive_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            post_links = soup.find_all('a', class_='post-preview-title')
            if not post_links:
                break
            
            tasks = [fetch_substack_post(client, urljoin(base_url, link['href'])) for link in post_links]
            batch_posts = await asyncio.gather(*tasks)
            posts.extend([post for post in batch_posts if post is not None])
            
            if len(posts) >= MAX_POSTS:
                posts = posts[:MAX_POSTS]
                break
            
            page += 1
    
    return {'posts': posts}

async def fetch_substack_post(client: httpx.AsyncClient, url: str) -> Dict[str, str]:
    try:
        response = await client.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.find('h1', class_='post-title').text.strip() if soup.find('h1', class_='post-title') else "Untitled"
        date = soup.find('time')['datetime'] if soup.find('time') else None
        content = soup.find('div', class_='post-content') or soup.find('div', class_='body')
        
        if not content:
            return None
        
        text = content.get_text(separator=' ', strip=True)
        
        return {
            'title': title,
            'url': url,
            'content': text,
            'date': date
        }
    except Exception as e:
        print(f"Error fetching {url}: {str(e)}")
        return None

# Helper function to convert scraper output to DataFrame
def scraper_output_to_df(data: Dict[str, List[Dict[str, str]]]) -> pd.DataFrame:
    return pd.DataFrame(data['posts'])
