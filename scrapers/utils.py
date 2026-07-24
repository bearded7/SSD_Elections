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
