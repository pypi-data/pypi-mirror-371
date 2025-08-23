from django.conf import settings
from django.contrib import auth
from django.utils.deprecation import MiddlewareMixin


class AuthenticateSessionMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if (hasattr(request, 'user') and request.user.is_authenticated) or \
            (
                settings.FORCE_SCRIPT_NAME and not request.path_info.lower().
            removeprefix(settings.FORCE_SCRIPT_NAME.lower()).
            startswith("/admin")
        ) or not request.path_info.lower().startswith("/admin"):
            return
        user = auth.authenticate(request)
        if hasattr(user, 'backend'):
            request._cached_user = user
            auth.login(
                request, user, user.backend)
