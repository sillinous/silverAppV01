import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def scrape_url(url: str) -> Dict[str, Any]:
    """
    Scrapes a URL for its textual content and image URLs using requests and BeautifulSoup.

    Args:
        url: The URL to scrape.

    Returns:
        A dictionary containing the scraped content as a string and a list of image URLs,
        or an empty string and empty list if scraping fails.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract image URLs
        image_urls = []
        for img in soup.find_all('img', src=True):
            src = img['src']
            # Make sure the URL is absolute
            if src.startswith('//'):
                src = 'http:' + src
            elif src.startswith('/'):
                src = requests.compat.urljoin(url, src)
            image_urls.append(src)

        # Remove script and style elements
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()

        # Get text and clean it up
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        cleaned_text = '\n'.join(chunk for chunk in chunks if chunk)

        return {"text": cleaned_text, "image_urls": image_urls}

    except requests.exceptions.RequestException as e:
        logger.error(f"Error scraping URL {url}: {e}")
        return {"text": "", "image_urls": []}


