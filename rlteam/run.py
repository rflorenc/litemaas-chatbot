#!/usr/bin/env python3
"""
Entry point for the Open Source Mentor Bot application.
This file is used by gunicorn in production and can be run directly for development.
"""

from app.main import app

if __name__ == '__main__':
    # For local development only
    # In production, use gunicorn (see Containerfile CMD)
    import os
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
