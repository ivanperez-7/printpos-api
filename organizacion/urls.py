from django.urls import path, include
from rest_framework import routers

from .views import *


router = routers.DefaultRouter()
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'users', UserViewSet, basename='usuario')
router.register(r'sucursales', SucursalViewSet, basename='sucursal')

urlpatterns = [
    path('', include(router.urls)),
]
