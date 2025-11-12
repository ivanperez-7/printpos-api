from django.urls import path, include
from rest_framework import routers

from .views import ProductoViewSet, CategoriaViewSet, MarcaViewSet, ProveedorViewSet


router = routers.DefaultRouter()
router.register(r'productos', ProductoViewSet)
router.register(r'categorias', CategoriaViewSet)
router.register(r'marcas', MarcaViewSet)
router.register(r'proveedores', ProveedorViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
