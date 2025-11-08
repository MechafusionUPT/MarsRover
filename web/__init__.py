# web/__init__.py

from .routes import init_routes
from .sockets import init_sockets

__all__ = ["init_routes", "init_sockets"]