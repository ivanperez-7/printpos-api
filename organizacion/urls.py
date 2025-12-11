from django.urls import path, include
from rest_framework import routers

from .views import *


router = routers.DefaultRouter()
router.register(r'clientes', ClienteViewSet, basename='producto')
router.register(r'users', UserViewSet, basename='lote')

urlpatterns = [
    path('', include(router.urls)),
]
