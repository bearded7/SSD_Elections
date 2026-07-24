"""
News scraping module for South Sudan sources
"""

import requests
import logging
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional
import time
import json
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

class NewsScraper:
    """Scrape news from South Sudan sources"""
    
    def __init__(self):
        self.ua = UserAgent()
        self.sources = self._load_sources()
        self.timeout = 10
        
    def _load_sources(self) -> List[Dict]:
        """Load source list from sources.json"""
        try:
            with open('sources.json', 'r') as f:
                data = json.load(f)
                return [s for s in data.get('news', []) 
                       if s.get('country') == 'South Sudan']
        except Exception as e:
            logger.error(f"Error loading sources: {e}")
            return []
    
    def fetch_rss(self, url: str) -> Optional[List[Dict]]:
        """Fetch and parse RSS feed"""
        try:
            headers = {'User-Agent': self.ua.random}
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'xml')
            items = []
            
            for item in soup.find_all('item')[:20]:
                items.append({
                    'title': item.title.text if item.title else '',
                    'link': item.link.text if item.link else '',
                    'pubDate': item.pubDate.text if item.pubDate else '',
                    'description': item.description.text[:500] if item.description else ''
                })
            
            return items
        except Exception as e:
            logger.error(f"Error fetching RSS from {url}: {e}")
            return None
    
    def scrape_website(self, url: str) -> Optional[List[Dict]]:
        """Scrape articles from website"""
        try:
            headers = {'User-Agent': self.ua.random}
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = []
            
            # Find article elements
            for article in soup.find_all('article')[:10]:
                title_tag = article.find(['h1', 'h2', 'h3'])
                link_tag = article.find('a')
                
                if title_tag and link_tag:
                    articles.append({
                        'title': title_tag.text.strip(),
                        'link': link_tag.get('href', ''),
                        'pubDate': None,
                        'description': None
                    })
            
            return articles
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None
    
    def get_all_news(self) -> List[Dict]:
        """Fetch news from all sources"""
        all_news = []
        
        for source in self.sources:
            logger.info(f"Fetching from {source['name']}")
            
            # Try RSS first
            if source.get('rss'):
                items = self.fetch_rss(source['rss'])
                if items:
                    all_news.extend(items)
                    continue
            
            # Fallback to website scraping
            if source.get('url'):
                items = self.scrape_website(source['url'])
                if items:
                    all_news.extend(items)
            
            # Rate limiting
            time.sleep(2)
        
        return all_news

# Utility function
def clean_text(text: str) -> str:
    """Clean text by removing extra whitespace and special characters"""
    if not text:
        return ""
    return ' '.join(text.strip().split())
