from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class AuthBurstThrottle(AnonRateThrottle):
    scope = 'auth_burst'


class AuthSustainedThrottle(UserRateThrottle):
    scope = 'auth_sustained'


class WriteBurstThrottle(UserRateThrottle):
    scope = 'write_burst'
