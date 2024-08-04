import httpx
from bs4 import BeautifulSoup

async def scrape_url(url: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract main content (this may need to be adjusted based on the structure of Medium/Substack pages)
        content = soup.find('article') or soup.find('div', class_='post-content')
        return content.get_text() if content else ""
