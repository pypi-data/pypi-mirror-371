from .api import routes as api_routes
from .docs import docs_routes

# Combine all routes
all_routes = api_routes + docs_routes
