from rest_framework.throttling import AnonRateThrottle, SimpleRateThrottle, UserRateThrottle


class AuthBurstThrottle(AnonRateThrottle):
    scope = 'auth_burst'


class AuthSustainedThrottle(UserRateThrottle):
    scope = 'auth_sustained'


class WriteBurstThrottle(UserRateThrottle):
    scope = 'write_burst'


class SearchThrottle(SimpleRateThrottle):
    scope = 'search'

    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        return self.cache_format % {'scope': self.scope, 'ident': ident}


class CatalogRetrieveThrottle(SimpleRateThrottle):
    scope = 'catalog_retrieve'

    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        return self.cache_format % {'scope': self.scope, 'ident': ident}
