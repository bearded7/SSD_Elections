"""
Entry point for Render deployment
This imports and runs the Dash app from app.py
"""

from app import app, server

if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 8050))
    debug = os.environ.get('ENVIRONMENT', 'development') == 'development'
    
    app.run(
        debug=debug,
        host='0.0.0.0',
        port=port
    )