from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import *


router = DefaultRouter()
router.register(r'entradas', EntradaInventarioViewSet, basename='entrada-inventario')
router.register(r'salidas', SalidaInventarioViewSet, basename='salida-inventario')

urlpatterns = [
    path('', include(router.urls)),
    path('main-table/', main_movements_table, name='main-movements-table'),
]
