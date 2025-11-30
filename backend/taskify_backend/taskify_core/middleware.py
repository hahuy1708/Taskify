# taskify_core/middleware.py
import threading
from django.utils.deprecation import MiddlewareMixin

_state = threading.local()


def get_current_user():
    return getattr(_state, "user", None)


def set_current_user(user):
    """Explicitly set current user in thread-local storage"""
    _state.user = user


class CurrentUserMiddleware(MiddlewareMixin):
    """
    Middleware to store authenticated user in thread-local storage.
    Note: For DRF+JWT, this captures user AFTER authentication is performed.
    """
    def process_request(self, request):
        _state.user = getattr(request, "user", None)
    
    def process_response(self, request, response):
        if hasattr(request, "user"):
            _state.user = request.user
        return response
    
    def process_exception(self, request, exception):
        _state.user = None
        return None
