from rest_framework.throttling import SimpleRateThrottle


class EvaluateRateThrottle(SimpleRateThrottle):
    """
    Custom throttle for the evaluate-user endpoint.

    Uses a stricter rate limit than the global default because
    each evaluation triggers DB queries + scoring computation.
    Rate is configured via THROTTLE_EVALUATE in settings (default: 60/minute).
    """

    scope = 'evaluate'

    def get_cache_key(self, request, view):
        """
        Rate-limit by IP for anonymous users,
        or by user ID for authenticated users.
        """
        if request.user and request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident,
        }
