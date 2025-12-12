from django.urls import path, include
from rest_framework import routers

from .views import *


router = routers.DefaultRouter()
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'lotes', LoteViewSet, basename='lote')
router.register(r'unidades', UnidadViewSet)
router.register(r'categorias', CategoriaViewSet)
router.register(r'marcas', MarcaViewSet)
router.register(r'equipos', EquipoViewSet)
router.register(r'proveedores', ProveedorViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', dashboard_view),
]
