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

    @action(detail=True, methods=['get', 'post'])
    def equipos(self, request, pk=None):
        if request.method == 'GET':
            # Obtener datos de uso del cliente
            productos = request.query_params.getlist('productos[]')
            cliente = self.get_object()

            if productos:
                qs = cliente.equipos.filter(equipo__producto__in=productos)
            else:
                qs = cliente.equipos.all()

            equipos = (
                qs.filter(equipo__activo=True, equipo__marca__activo=True)
                .values('id', 'equipo__id', 'equipo__nombre', 'contador_uso', 'alias')
                .distinct()
            )
            return Response(equipos)

        if request.method == 'POST':
            # Crear equipos del cliente
            cliente = self.get_object()
            cliente.equipos.create(
                equipo_id=request.data['equipoId'],
                contador_uso=request.data['contadorUso'],
                alias=request.data.get('alias', '')
            )
            return Response({'success': True}, status=201)

        return Response(status=405)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
