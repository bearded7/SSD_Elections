#!/bin/bash

# South Sudan Election Monitor - Project Setup Script
# This will create the complete project structure with all files

set -e

PROJECT_NAME="SSD_Elections"
echo "🚀 Setting up $PROJECT_NAME project..."

# Create main directory
mkdir -p $PROJECT_NAME
cd $PROJECT_NAME

# Create directory structure
mkdir -p scrapers utils assets templates data/cache data/exports tests logs

# Create __init__.py files
touch scrapers/__init__.py utils/__init__.py tests/__init__.py

# Create placeholder files
touch assets/style.css assets/favicon.ico
touch logs/app.log
touch data/.gitkeep
touch templates/index.html

# Create app.py
cat > app.py << 'EOF'
"""
South Sudan Election Monitoring Dashboard
Main Dash Application
"""

import os
import json
import logging
from datetime import datetime
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}]
)
server = app.server  # For gunicorn deployment

# Load sources configuration
def load_sources():
    """Load sources from JSON file"""
    try:
        with open('sources.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("sources.json not found!")
        return {"news": [], "government": [], "ngo": []}
    except json.JSONDecodeError:
        logger.error("Invalid JSON in sources.json!")
        return {"news": [], "government": [], "ngo": []}

SOURCES = load_sources()

# App Layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col(
            html.Div([
                html.H1("🗳️ South Sudan Election Monitor", 
                       className="text-center text-primary mb-0"),
                html.P("Real-time election monitoring dashboard", 
                       className="text-center text-muted")
            ]),
            width=12
        )
    ], className="mb-4"),
    
    # Stats Row
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Total Sources", className="card-title"),
                html.H2(len(SOURCES.get('news', [])) + 
                       len(SOURCES.get('government', [])) + 
                       len(SOURCES.get('ngo', [])), 
                       className="text-primary")
            ])
        ]), md=3),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("News Sources", className="card-title"),
                html.H2(len(SOURCES.get('news', [])), className="text-success")
            ])
        ]), md=3),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Official Sources", className="card-title"),
                html.H2(len(SOURCES.get('government', [])), className="text-warning")
            ])
        ]), md=3),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("NGO Sources", className="card-title"),
                html.H2(len(SOURCES.get('ngo', [])), className="text-info")
            ])
        ]), md=3)
    ], className="mb-4"),
    
    # Tabs
    dbc.Tabs([
        dbc.Tab(label="News Sources", tab_id="tab-news", children=[
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H4("South Sudan News Sources", className="mt-3"),
                        html.Ul([
                            html.Li([
                                html.A(source['name'], href=source['url'], target="_blank"),
                                " - ",
                                html.Small(source.get('country', 'Unknown'), 
                                         className="badge badge-secondary"),
                                html.Br(),
                                html.Small(f"RSS: {source.get('rss', 'N/A')}", 
                                         className="text-muted")
                            ])
                            for source in SOURCES.get('news', [])
                        ], className="list-group list-group-flush")
                    ])
                ], md=8),
                dbc.Col([
                    html.Div([
                        html.H4("Source Distribution", className="mt-3"),
                        dcc.Graph(
                            figure=px.pie(
                                names=['News', 'Government', 'NGO'],
                                values=[
                                    len(SOURCES.get('news', [])),
                                    len(SOURCES.get('government', [])),
                                    len(SOURCES.get('ngo', []))
                                ],
                                title="Source Type Distribution"
                            )
                        )
                    ])
                ], md=4)
            ])
        ]),
        
        dbc.Tab(label="Official Sources", tab_id="tab-official", children=[
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H4("Government & Electoral Bodies", className="mt-3"),
                        html.Ul([
                            html.Li([
                                html.A(source['name'], href=source['url'], target="_blank"),
                                " - ",
                                html.Span(source.get('category', ''), 
                                        className="badge badge-info")
                            ])
                            for source in SOURCES.get('government', [])
                        ], className="list-group list-group-flush")
                    ])
                ], md=6),
                dbc.Col([
                    html.Div([
                        html.H4("NGOs & Organizations", className="mt-3"),
                        html.Ul([
                            html.Li([
                                html.A(source['name'], href=source['url'], target="_blank"),
                                " - ",
                                html.Span(source.get('category', ''), 
                                        className="badge badge-success")
                            ])
                            for source in SOURCES.get('ngo', [])
                        ], className="list-group list-group-flush")
                    ])
                ], md=6)
            ])
        ]),
        
        dbc.Tab(label="Reliability Analysis", tab_id="tab-reliability", children=[
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H4("Source Reliability Ratings", className="mt-3"),
                        dcc.Graph(
                            figure=px.bar(
                                x=list(SOURCES.get('reliability_ratings', {}).keys()),
                                y=[{'high': 3, 'medium': 2, 'low': 1}
                                   .get(v, 0) for v in SOURCES.get('reliability_ratings', {}).values()],
                                labels={'x': 'Source', 'y': 'Reliability Score'},
                                title="Source Reliability"
                            )
                        )
                    ])
                ], md=12),
                dbc.Col([
                    html.Div([
                        html.H4("Keyword Categories", className="mt-3"),
                        html.Div([
                            html.H6("Election Terms"),
                            html.P(", ".join(SOURCES.get('keywords', {})
                                           .get('election_related', [])[:10]))
                        ], className="mb-2"),
                        html.Div([
                            html.H6("Political Terms"),
                            html.P(", ".join(SOURCES.get('keywords', {})
                                           .get('political_related', [])[:10]))
                        ], className="mb-2"),
                        html.Div([
                            html.H6("Security Terms"),
                            html.P(", ".join(SOURCES.get('keywords', {})
                                           .get('security_related', [])[:10]))
                        ], className="mb-2")
                    ])
                ], md=12)
            ])
        ]),
        
        dbc.Tab(label="About", tab_id="tab-about", children=[
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H4("About This Dashboard", className="mt-3"),
                        html.P("""
                            The South Sudan Election Monitoring Dashboard aggregates news, 
                            official statements, and NGO reports to provide comprehensive 
                            coverage of the electoral process in South Sudan.
                        """),
                        html.H5("Features:"),
                        html.Ul([
                            html.Li("Real-time news aggregation from South Sudanese sources"),
                            html.Li("Official government and electoral body monitoring"),
                            html.Li("NGO and international organization reports"),
                            html.Li("Reliability scoring for different source types"),
                            html.Li("Keyword tracking for election-related terms")
                        ]),
                        html.H5("Data Sources:"),
                        html.P("Sources are curated from verified news outlets, "
                              "government websites, and reputable NGOs operating in South Sudan."),
                        html.Hr(),
                        html.P("Last Updated: " + 
                              datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                              className="text-muted")
                    ])
                ], md=12)
            ])
        ])
    ], id="tabs", active_tab="tab-news"),
    
    # Footer
    dbc.Row([
        dbc.Col(
            html.P("© 2026 South Sudan Election Monitor | Data refreshed hourly", 
                   className="text-center text-muted mt-4"),
            width=12
        )
    ])
], fluid=True, className="p-3")

# Callbacks
@callback(
    Output("tabs", "active_tab"),
    Input("tabs", "active_tab")
)
def update_tab(tab):
    """Handle tab switching"""
    logger.info(f"Tab changed to: {tab}")
    return tab

# Main entry point
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    debug = os.environ.get('ENVIRONMENT', 'development') == 'development'
    
    logger.info(f"Starting app on port {port}")
    app.run(
        debug=debug,
        host='0.0.0.0',
        port=port
    )
EOF

# Create requirements.txt
cat > requirements.txt << 'EOF'
# Web Framework
dash==2.14.0
dash-bootstrap-components==1.5.0
plotly==5.18.0
gunicorn==21.2.0

# Data Processing
pandas==2.0.3
numpy==1.24.3

# Web Scraping
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3
fake-useragent==1.4.0

# NLP (lightweight)
textblob==0.17.1
nltk==3.8.1

# Utilities
python-dotenv==1.0.0
schedule==1.2.0
pdfplumber==0.10.3

# API & GitHub
PyGithub==1.59.0

# CORS
cors==1.0.1

# Testing (optional)
pytest==7.4.0
EOF

# Create sources.json
cat > sources.json << 'EOF'
{
  "news": [
    {
      "name": "Radio Tamazuj",
      "url": "https://radiotamazuj.org/en/",
      "rss": "https://radiotamazuj.org/en/feed/",
      "type": "news",
      "country": "South Sudan"
    },
    {
      "name": "Eye Radio Juba",
      "url": "https://eyeradio.org/",
      "rss": "https://eyeradio.org/feed/",
      "type": "news",
      "country": "South Sudan"
    },
    {
      "name": "Sudans Post",
      "url": "https://www.sudanspost.com/",
      "rss": "https://www.sudanspost.com/feed/",
      "type": "news",
      "country": "South Sudan"
    },
    {
      "name": "The City Review",
      "url": "https://thecityreview.com/",
      "rss": "https://thecityreview.com/feed/",
      "type": "news",
      "country": "South Sudan"
    },
    {
      "name": "Gurtong",
      "url": "http://www.gurtong.net/",
      "rss": "http://www.gurtong.net/RSS/RSSNews.aspx",
      "type": "news",
      "country": "South Sudan"
    },
    {
      "name": "South Sudan News Agency",
      "url": "https://www.southsudannewsagency.com/",
      "rss": "https://www.southsudannewsagency.com/feed/",
      "type": "news",
      "country": "South Sudan"
    },
    {
      "name": "Hot in Juba",
      "url": "https://hotinjuba.com/",
      "rss": "https://hotinjuba.com/feed/",
      "type": "news",
      "country": "South Sudan"
    },
    {
      "name": "Xinhua Africa",
      "url": "https://www.xinhuanet.com/english/africa/",
      "rss": "http://www.xinhuanet.com/english/africa/index.xml",
      "type": "news",
      "country": "China"
    },
    {
      "name": "BBC Africa",
      "url": "https://www.bbc.com/news/world/africa",
      "rss": "http://feeds.bbci.co.uk/news/world/africa/rss.xml",
      "type": "news",
      "country": "UK"
    },
    {
      "name": "Reuters Africa",
      "url": "https://www.reuters.com/world/africa/",
      "rss": "https://www.reuters.com/world/africa/?format=rss",
      "type": "news",
      "country": "Global"
    }
  ],
  "government": [
    {
      "name": "NEC South Sudan",
      "url": "https://necss.gov.ss",
      "type": "official",
      "category": "electoral"
    },
    {
      "name": "SSBC",
      "url": "https://ssbc.gov.ss",
      "type": "official",
      "category": "broadcasting"
    },
    {
      "name": "Political Parties Council",
      "url": "https://ppc.gov.ss",
      "type": "official",
      "category": "political"
    }
  ],
  "ngo": [
    {
      "name": "UNMISS",
      "url": "https://unmiss.unmissions.org",
      "rss": "https://unmiss.unmissions.org/rss.xml",
      "type": "ngo",
      "category": "peacekeeping"
    },
    {
      "name": "FES South Sudan",
      "url": "https://www.fes-sudans.org",
      "type": "ngo",
      "category": "research"
    },
    {
      "name": "PeaceRep",
      "url": "https://peacerep.org/research/south-sudan/",
      "type": "ngo",
      "category": "research"
    },
    {
      "name": "International Crisis Group",
      "url": "https://www.crisisgroup.org/africa/horn-africa/south-sudan",
      "type": "ngo",
      "category": "research"
    },
    {
      "name": "UNDP South Sudan",
      "url": "https://www.undp.org/south-sudan",
      "type": "ngo",
      "category": "development"
    },
    {
      "name": "Human Rights Watch",
      "url": "https://www.hrw.org/africa/south-sudan",
      "type": "ngo",
      "category": "human_rights"
    }
  ],
  "social_media": [
    {
      "name": "Twitter/X",
      "type": "social_media",
      "api_endpoint": "https://api.twitter.com/2",
      "rate_limit": 300
    },
    {
      "name": "Facebook",
      "type": "social_media",
      "api_endpoint": "https://graph.facebook.com",
      "rate_limit": 200
    }
  ],
  "source_weights": {
    "official": 1.0,
    "news": 0.8,
    "ngo": 0.85,
    "social_media": 0.5
  },
  "reliability_ratings": {
    "nec": "high",
    "unmiss": "high",
    "fes": "high",
    "peacerep": "high",
    "xinhua": "medium",
    "anadolu": "medium",
    "radiotamazuj": "medium",
    "twitter": "low",
    "facebook": "low"
  },
  "keywords": {
    "election_related": [
      "election",
      "vote",
      "ballot",
      "poll",
      "candidate",
      "party",
      "register",
      "voter",
      "democracy",
      "transition"
    ],
    "security_related": [
      "peace",
      "security",
      "violence",
      "conflict",
      "stable",
      "unrest",
      "peacekeeping",
      "force",
      "military"
    ],
    "political_related": [
      "kiir",
      "machar",
      "splm",
      "splm-io",
      "ssoa",
      "government",
      "opposition",
      "negotiation",
      "dialogue"
    ],
    "technical_related": [
      "registration",
      "funding",
      "budget",
      "timeline",
      "readiness",
      "preparedness",
      "logistics",
      "infrastructure"
    ]
  }
}
EOF

# Create render.yaml
cat > render.yaml << 'EOF'
services:
  - type: web
    name: ssd-election-monitor
    env: python
    plan: free
    buildCommand: |
      pip install --upgrade pip
      pip install -r requirements.txt
      python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"
    startCommand: gunicorn app:server --worker-class gthread --workers 1 --threads 4 --timeout 120
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.0
      - key: ENVIRONMENT
        value: production
      - key: PORT
        value: 8050
    healthCheckPath: /
    autoDeploy: true
EOF

# Create Procfile
cat > Procfile << 'EOF'
web: gunicorn app:server --worker-class gthread --workers 1 --threads 4 --timeout 120 --bind 0.0.0.0:$PORT
EOF

# Create .env.example
cat > .env.example << 'EOF'
# App Configuration
PORT=8050
ENVIRONMENT=production
SECRET_KEY=your-secret-key-here

# API Keys (if needed)
GITHUB_TOKEN=your-github-token
TWITTER_API_KEY=your-twitter-api-key
TWITTER_API_SECRET=your-twitter-api-secret

# Optional: Database (if using)
DATABASE_URL=sqlite:///data/election.db

# Logging
LOG_LEVEL=INFO
EOF

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment
.env
.venv
.env.local
.env.*.local

# Logs
logs/
*.log
*.log.*

# Data
data/cache/
data/exports/
*.db
*.sqlite
*.sqlite3

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# OS
Thumbs.db
*.bak

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Jupyter Notebooks
.ipynb_checkpoints/

# Misc
*.pem
*.p12
*.key
*.p7b
EOF

# Create scrapers files
cat > scrapers/__init__.py << 'EOF'
"""
Scrapers module for South Sudan Election Monitor
"""

from .news_scraper import NewsScraper
from .social_scraper import SocialScraper
from .utils import clean_text, extract_date

__all__ = ['NewsScraper', 'SocialScraper', 'clean_text', 'extract_date']
EOF

cat > scrapers/news_scraper.py << 'EOF'
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
EOF

cat > scrapers/social_scraper.py << 'EOF'
"""
Social media scraping module
"""

import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class SocialScraper:
    """Scrape social media for election-related content"""
    
    def __init__(self):
        self.keywords = self._load_keywords()
    
    def _load_keywords(self) -> List[str]:
        """Load keywords from sources.json"""
        try:
            import json
            with open('sources.json', 'r') as f:
                data = json.load(f)
                return data.get('keywords', {}).get('election_related', [])
        except:
            return []
    
    def search_twitter(self, query: str) -> List[Dict]:
        """Search Twitter API (placeholder)"""
        logger.info(f"Searching Twitter for: {query}")
        # Implementation would require Twitter API credentials
        return []
    
    def search_facebook(self, query: str) -> List[Dict]:
        """Search Facebook API (placeholder)"""
        logger.info(f"Searching Facebook for: {query}")
        # Implementation would require Facebook API credentials
        return []
EOF

cat > scrapers/utils.py << 'EOF'
"""
Utility functions for scrapers
"""

import re
from datetime import datetime
from typing import Optional

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    # Remove extra whitespace
    text = ' '.join(text.split())
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()

def extract_date(text: str) -> Optional[datetime]:
    """Extract date from text"""
    date_patterns = [
        r'(\d{4}-\d{2}-\d{2})',
        r'(\d{2}/\d{2}/\d{4})',
        r'(\d{1,2}\s+[A-Za-z]+\s+\d{4})'
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                return datetime.strptime(match.group(1), '%Y-%m-%d')
            except:
                continue
    return None

def validate_url(url: str) -> bool:
    """Validate if URL is properly formatted"""
    pattern = re.compile(
        r'^https?://' 
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    return bool(pattern.match(url))
EOF

# Create utils files
cat > utils/__init__.py << 'EOF'
"""
Utility functions module
"""

from .data_processor import DataProcessor
from .validators import validate_email, validate_date

__all__ = ['DataProcessor', 'validate_email', 'validate_date']
EOF

cat > utils/data_processor.py << 'EOF'
"""
Data processing utilities
"""

import pandas as pd
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class DataProcessor:
    """Process and analyze election data"""
    
    @staticmethod
    def categorize_articles(articles: List[Dict]) -> pd.DataFrame:
        """Categorize articles by topic"""
        df = pd.DataFrame(articles)
        
        # Add category column
        def categorize(title):
            title_lower = str(title).lower()
            if any(word in title_lower for word in ['election', 'vote', 'poll']):
                return 'Election'
            elif any(word in title_lower for word in ['peace', 'security', 'violence']):
                return 'Security'
            elif any(word in title_lower for word in ['kiir', 'machar', 'splm']):
                return 'Political'
            return 'General'
        
        df['category'] = df['title'].apply(categorize)
        return df
    
    @staticmethod
    def get_source_stats(sources: List[Dict]) -> Dict:
        """Get statistics about sources"""
        stats = {
            'total': len(sources),
            'by_country': {},
            'by_type': {}
        }
        
        for source in sources:
            country = source.get('country', 'Unknown')
            stats['by_country'][country] = stats['by_country'].get(country, 0) + 1
            
            source_type = source.get('type', 'unknown')
            stats['by_type'][source_type] = stats['by_type'].get(source_type, 0) + 1
        
        return stats
EOF

cat > utils/validators.py << 'EOF'
"""
Validation utilities
"""

import re
from datetime import datetime

def validate_email(email: str) -> bool:
    """Validate email address"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_date(date_str: str, format: str = '%Y-%m-%d') -> bool:
    """Validate date string"""
    try:
        datetime.strptime(date_str, format)
        return True
    except ValueError:
        return False
EOF

# Create assets
cat > assets/style.css << 'EOF'
/* Custom styling for South Sudan Election Monitor */

body {
    background-color: #f8f9fa;
}

.card {
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    border: none;
    margin-bottom: 20px;
}

.card-header {
    background-color: #2c3e50;
    color: white;
    font-weight: bold;
}

.badge {
    font-size: 0.7rem;
    padding: 0.3rem 0.6rem;
}

.list-group-item {
    background-color: transparent;
    border-left: none;
    border-right: none;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .container-fluid {
        padding: 10px;
    }
}

/* Custom colors */
.text-primary {
    color: #3498db !important;
}

.bg-primary {
    background-color: #3498db !important;
}

.text-success {
    color: #2ecc71 !important;
}

.text-warning {
    color: #f39c12 !important;
}

.text-info {
    color: #1abc9c !important;
}

/* Footer styling */
.footer {
    margin-top: 40px;
    padding: 20px 0;
    border-top: 1px solid #dee2e6;
}
EOF

# Create run.py
cat > run.py << 'EOF'
#!/usr/bin/env python
"""
Alternative startup script for local development
"""

import os
import sys
from app import app

def main():
    """Run the application"""
    port = int(os.environ.get('PORT', 8050))
    debug = os.environ.get('ENVIRONMENT', 'development') == 'development'
    
    print(f"🚀 Starting South Sudan Election Monitor on port {port}")
    print(f"📊 Debug mode: {debug}")
    print(f"🌐 Open http://localhost:{port} in your browser")
    
    app.run(
        debug=debug,
        host='0.0.0.0',
        port=port
    )

if __name__ == '__main__':
    main()
EOF

# Create README.md
cat > README.md << 'EOF'
# South Sudan Election Monitor

A comprehensive election monitoring dashboard for South Sudan, aggregating news, official statements, and NGO reports.

## Features

- 📰 Real-time news aggregation from South Sudanese sources
- 🏛️ Official government and electoral body monitoring
- 🌍 NGO and international organization reports
- 📊 Source reliability scoring
- 🔍 Keyword tracking for election-related terms
- 📱 Mobile-responsive design

## Technology Stack

- **Framework**: Dash/Plotly
- **Scraping**: BeautifulSoup4, Requests
- **Data Processing**: Pandas, Numpy
- **Deployment**: Render.com
- **Language**: Python 3.9+

## Local Development

### Installation

```bash
# Clone repository
git clone https://github.com/bearded7/SSD_Elections.git
cd SSD_Elections

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run locally
python app.py