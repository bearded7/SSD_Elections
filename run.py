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
