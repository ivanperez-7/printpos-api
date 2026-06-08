from rest_framework.throttling import AnonRateThrottle


class SucursalAnonThrottle(AnonRateThrottle):
    scope = 'sucursales'
