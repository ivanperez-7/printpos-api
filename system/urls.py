from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AlertaViewSet, ConfiguracionSistemaViewSet, RegistroActividadViewSet

router = DefaultRouter()
router.register(r'configuracion', ConfiguracionSistemaViewSet, basename='configuracion')
router.register(r'alertas', AlertaViewSet, basename='alertas')
router.register(r'actividades', RegistroActividadViewSet, basename='actividades')

urlpatterns = [
    path('', include(router.urls)),
]
