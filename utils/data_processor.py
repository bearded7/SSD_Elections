"""
Data processing utilities with sentiment analysis
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import logging
from textblob import TextBlob
import re

logger = logging.getLogger(__name__)

class DataProcessor:
    """Process and analyze election data with sentiment"""
    
    def __init__(self):
        # Load keywords from sources.json
        try:
            import json
            with open('sources.json', 'r') as f:
                data = json.load(f)
                self.keywords = data.get('keywords', {})
        except:
            self.keywords = {}
    
    def categorize_articles(self, articles: List[Dict]) -> pd.DataFrame:
        """Categorize articles by topic"""
        if not articles:
            return pd.DataFrame()
        
        df = pd.DataFrame(articles)
        
        # Add category column
        def categorize(title):
            title_lower = str(title).lower()
            election_terms = self.keywords.get('election_related', [])
            political_terms = self.keywords.get('political_related', [])
            security_terms = self.keywords.get('security_related', [])
            
            if any(word in title_lower for word in election_terms):
                return 'Election'
            elif any(word in title_lower for word in political_terms):
                return 'Political'
            elif any(word in title_lower for word in security_terms):
                return 'Security'
            return 'General'
        
        df['category'] = df['title'].apply(categorize)
        return df
    
    def analyze_sentiment(self, texts: List[str]) -> List[str]:
        """Analyze sentiment of text using TextBlob"""
        sentiments = []
        for text in texts:
            try:
                blob = TextBlob(str(text))
                polarity = blob.sentiment.polarity
                if polarity > 0.1:
                    sentiments.append('Positive')
                elif polarity < -0.1:
                    sentiments.append('Negative')
                else:
                    sentiments.append('Neutral')
            except:
                sentiments.append('Neutral')
        return sentiments
    
    def get_sentiment_emoji(self, text: str) -> str:
        """Get sentiment emoji for text"""
        try:
            blob = TextBlob(str(text))
            polarity = blob.sentiment.polarity
            if polarity > 0.1:
                return "😊"
            elif polarity < -0.1:
                return "😟"
            else:
                return "😐"
        except:
            return "😐"
    
    def calculate_sentiment_score(self, sentiments: List[str]) -> Dict:
        """Calculate sentiment distribution"""
        if not sentiments:
            return {'positive': 0, 'negative': 0, 'neutral': 0}
        
        total = len(sentiments)
        positive = sum(1 for s in sentiments if s == 'Positive')
        negative = sum(1 for s in sentiments if s == 'Negative')
        neutral = total - positive - negative
        
        return {
            'positive': round(positive / total * 100, 1),
            'negative': round(negative / total * 100, 1),
            'neutral': round(neutral / total * 100, 1)
        }
    
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
    
    def calculate_election_probability(self, article_data: List[Dict]) -> Dict:
        """Calculate probability of elections being held"""
        if not article_data:
            return {'probability': 50, 'factors': []}
        
        # Define positive and negative indicators
        positive_indicators = [
            'prepared', 'ready', 'progress', 'on track', 
            'registration', 'voter', 'peaceful', 'stable'
        ]
        negative_indicators = [
            'delay', 'postpone', 'violence', 'conflict',
            'dispute', 'uncertainty', 'concern', 'risk'
        ]
        
        # Count indicators
        positive_count = 0
        negative_count = 0
        
        for article in article_data:
            text = str(article.get('title', '')) + ' ' + str(article.get('description', ''))
            text_lower = text.lower()
            
            for indicator in positive_indicators:
                if indicator in text_lower:
                    positive_count += 1
            
            for indicator in negative_indicators:
                if indicator in text_lower:
                    negative_count += 1
        
        total_indicators = positive_count + negative_count
        if total_indicators == 0:
            probability = 50
        else:
            probability = (positive_count / total_indicators) * 100
        
        # Consider time factor
        from datetime import datetime
        target_date = datetime(2026, 12, 22)
        days_remaining = (target_date - datetime.now()).days
        time_factor = min(100, max(0, (365 - days_remaining) / 365 * 100))
        
        # Combine factors
        final_probability = (probability * 0.7) + (time_factor * 0.3)
        
        return {
            'probability': round(min(100, final_probability), 1),
            'positive_indicators': positive_count,
            'negative_indicators': negative_count,
            'articles_analyzed': len(article_data),
            'days_remaining': days_remaining
        }