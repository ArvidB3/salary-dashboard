from flask_caching import Cache

cache = Cache(config={"CACHE_TYPE": "filesystem", "CACHE_DIR": "/tmp"})

def init_cache(app):
    """Attach cache to Dash app"""
    cache.init_app(app.server, config={"CACHE_TYPE": "simple"})  # Attach to Flask server
