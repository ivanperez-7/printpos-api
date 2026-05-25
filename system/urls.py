from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AlertaViewSet, ConfiguracionSistemaViewSet

router = DefaultRouter()
router.register(r'configuracion', ConfiguracionSistemaViewSet, basename='configuracion')
router.register(r'alertas', AlertaViewSet, basename='alertas')

urlpatterns = [
    path('', include(router.urls)),
]
