"""
News scraping module for South Sudan sources
Enhanced with better error handling and retry logic
"""

import requests
import logging
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional
import time
import json
from fake_useragent import UserAgent
import random

logger = logging.getLogger(__name__)

class NewsScraper:
    """Scrape news from South Sudan sources with retry logic"""
    
    def __init__(self):
        self.ua = UserAgent()
        self.sources = self._load_sources()
        self.timeout = 15
        self.max_retries = 3
        self.delay = 2
        
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
    
    def _make_request(self, url: str) -> Optional[requests.Response]:
        """Make HTTP request with retry logic"""
        for attempt in range(self.max_retries):
            try:
                headers = {
                    'User-Agent': self.ua.random,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                }
                
                response = requests.get(
                    url, 
                    headers=headers, 
                    timeout=self.timeout,
                    allow_redirects=True
                )
                response.raise_for_status()
                return response
                
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                time.sleep(self.delay * (attempt + 1))
                
        return None
    
    def fetch_rss(self, url: str) -> Optional[List[Dict]]:
        """Fetch and parse RSS feed"""
        response = self._make_request(url)
        if not response:
            return None
        
        try:
            soup = BeautifulSoup(response.content, 'xml')
            items = []
            
            for item in soup.find_all('item')[:20]:
                title = item.title.text if item.title else ''
                link = item.link.text if item.link else ''
                pub_date = item.pubDate.text if item.pubDate else ''
                description = item.description.text[:500] if item.description else ''
                
                # Extract date
                try:
                    date = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
                except:
                    date = datetime.now()
                
                items.append({
                    'title': title.strip(),
                    'link': link.strip(),
                    'pubDate': date.isoformat() if date else None,
                    'description': description.strip(),
                    'source': url.split('/')[2] if url else 'Unknown'
                })
            
            return items
        except Exception as e:
            logger.error(f"Error parsing RSS from {url}: {e}")
            return None
    
    def scrape_website(self, url: str) -> Optional[List[Dict]]:
        """Scrape articles from website"""
        response = self._make_request(url)
        if not response:
            return None
        
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = []
            
            # Try different selectors for articles
            selectors = ['article', '.post', '.entry', '.news-item', '.story']
            found_articles = []
            
            for selector in selectors:
                found = soup.select(selector)
                if found:
                    found_articles.extend(found)
                    break
            
            if not found_articles:
                # Try finding by common patterns
                for tag in soup.find_all(['h2', 'h3']):
                    parent = tag.find_parent()
                    if parent and parent.find('a'):
                        found_articles.append(parent)
            
            for article in found_articles[:10]:
                title_tag = article.find(['h1', 'h2', 'h3'])
                link_tag = article.find('a')
                
                if title_tag and link_tag:
                    title = title_tag.text.strip()
                    link = link_tag.get('href', '')
                    
                    # Make absolute URL if relative
                    if link and not link.startswith('http'):
                        from urllib.parse import urljoin
                        link = urljoin(url, link)
                    
                    articles.append({
                        'title': title,
                        'link': link,
                        'pubDate': datetime.now().isoformat(),
                        'description': None,
                        'source': url.split('/')[2] if url else 'Unknown'
                    })
            
            return articles
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None
    
    def get_all_news(self) -> List[Dict]:
        """Fetch news from all sources with rate limiting"""
        all_news = []
        
        for source in self.sources:
            logger.info(f"Fetching from {source['name']}")
            articles = []
            
            # Try RSS first
            if source.get('rss'):
                articles = self.fetch_rss(source['rss'])
            
            # Fallback to website scraping
            if not articles and source.get('url'):
                articles = self.scrape_website(source['url'])
            
            if articles:
                # Add source name to each article
                for article in articles:
                    article['source'] = source['name']
                    article['source_type'] = source.get('type', 'news')
                    article['country'] = source.get('country', 'Unknown')
                
                all_news.extend(articles)
                logger.info(f"Fetched {len(articles)} articles from {source['name']}")
            else:
                logger.warning(f"No articles fetched from {source['name']}")
            
            # Random delay between sources
            time.sleep(random.uniform(1, 3))
        
        logger.info(f"Total fetched: {len(all_news)} articles")
        return all_news