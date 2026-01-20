from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Cliente
from .serializers import *

__all__ = ['ClienteViewSet', 'UserViewSet']


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.filter(activo=True)
    serializer_class = ClienteSerializer
    
    @action(detail=True, methods=['get'])
    def equipos(self, request, pk=None):
        productos = request.query_params.getlist('productos[]')
        if not productos:
            return Response(data={"detail": "El parámetro 'productos' no vacío es obligatorio."}, status=400)
        
        cliente = self.get_object()
        equipos = cliente.equipos.filter(pk__in=productos).values('equipo__id', 'equipo__nombre', 'contador_uso')
        return Response(data=equipos)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
