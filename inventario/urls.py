from django.urls import path, include
from rest_framework import routers

from .views import *


router = routers.DefaultRouter()
router.register('productos', ProductoViewSet)
router.register('inventario', InventarioViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
