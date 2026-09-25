import os
import sys

# Ensure project root directory is on sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app

# WSGI Middleware to normalize Vercel serverless function route prefixes
class VercelPathNormalizer:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '')
        if path_info in ('/api/index', '/api/index.py', '/api', '/api/'):
            environ['PATH_INFO'] = '/'
        elif path_info.startswith('/api/index/'):
            environ['PATH_INFO'] = path_info[len('/api/index'):]
        elif path_info.startswith('/api/index.py/'):
            environ['PATH_INFO'] = path_info[len('/api/index.py'):]
        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathNormalizer(app.wsgi_app)

# Vercel detects and invokes 'app'
