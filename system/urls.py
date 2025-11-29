from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ConfiguracionSistemaViewSet

router = DefaultRouter()
router.register(r'configuracion', ConfiguracionSistemaViewSet, basename='configuracion')

urlpatterns = [
    path('', include(router.urls)),
]
