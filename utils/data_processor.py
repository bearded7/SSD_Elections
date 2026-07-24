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
