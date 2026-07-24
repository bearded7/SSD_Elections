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
