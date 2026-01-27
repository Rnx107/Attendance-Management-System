from base64 import b64decode
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from rest_framework import authentication, exceptions

from .models import ApiKey


class StaticApiKeyAndBasicAuthentication(authentication.BaseAuthentication):
    """Authentication that requires a valid X-API-KEY header.

    If a Basic `Authorization` header is provided, tries to authenticate the
    user for that request and returns the user. If Basic auth is absent, the
    request is still accepted as long as the API key matches; the returned
    user will be `AnonymousUser()` which allows views to decide.
    """

    def authenticate(self, request):
        api_key = None
        # prefer META header lookup for compatibility
        if 'HTTP_X_API_KEY' in request.META:
            api_key = request.META.get('HTTP_X_API_KEY')
        else:
            # Django request.headers is available in newer versions
            api_key = getattr(request, 'headers', {}).get('X-API-KEY')

        current = ApiKey.get_solo()
        if not api_key or not current.key or api_key != current.key:
            raise exceptions.AuthenticationFailed('Invalid or missing API key')

        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header:
            return (AnonymousUser(), None)

        try:
            auth_type, creds = auth_header.split(' ', 1)
            if auth_type.lower() != 'basic':
                return (AnonymousUser(), None)
            decoded = b64decode(creds).decode('utf-8')
            username, password = decoded.split(':', 1)
        except Exception:
            raise exceptions.AuthenticationFailed('Invalid Authorization header')

        user = authenticate(request, username=username, password=password)
        if user is None:
            raise exceptions.AuthenticationFailed('Invalid username/password')

        return (user, None)
