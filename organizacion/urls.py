from django.urls import path, include
from rest_framework import routers

from .views import *


router = routers.DefaultRouter()
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'users', UserViewSet, basename='usuario')

urlpatterns = [
    path('', include(router.urls)),
]
