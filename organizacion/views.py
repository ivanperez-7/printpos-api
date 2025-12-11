from django.contrib.auth.models import User
from rest_framework import viewsets

from .models import Cliente
from .serializers import *

__all__ = ['ClienteViewSet', 'UserViewSet']


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.filter(activo=True)
    serializer_class = ClienteSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
