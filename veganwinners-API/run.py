#!/usr/bin/env python

from app import app
from os import environ

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(environ.get('PORT', 80))
    app.run(host='0.0.0.0', port=port, debug=True)