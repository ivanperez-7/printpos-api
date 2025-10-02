from django.urls import path, include
from rest_framework import routers

from .views import *

router = routers.DefaultRouter()
router.register('ventas', VentaViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('get-usuario-pendientes/', get_usuario_pendientes, name='get-usuario-pendientes'),
]
