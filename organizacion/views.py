from django.contrib.auth.models import User
from django.db.models import F
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from system.models import RegistroActividad
from utils.mixins import ActivityLogMixin

from .models import EquipoCliente
from .queries import clientes_queryset
from .serializers import *
from productos.serializers import EquipoClienteSerializer

__all__ = ['ClienteViewSet', 'UserViewSet', 'SucursalViewSet']


class ClienteViewSet(ActivityLogMixin, viewsets.ModelViewSet):
    serializer_class = ClienteSerializer

    def get_queryset(self):
        return clientes_queryset(self.request.branch_id)

    # Se sobreescribe perform_update para detectar soft-delete
    # (activo True → False) y registrarlo como 'delete' en lugar de 'update'.
    def perform_update(self, serializer):
        old_active = serializer.instance.activo
        instance = serializer.save()
        action = 'delete' if old_active and not instance.activo else 'update'
        self.log(instance, action)

    @action(detail=True, methods=['get', 'post', 'delete'])
    def equipos(self, request, pk=None):
        if request.method == 'GET':
            # Obtener datos de uso del cliente
            productos = request.query_params.getlist('productos[]')
            cliente = self.get_object()

            if productos:
                qs = cliente.equipos.filter(equipo__producto__in=productos)
            else:
                qs = cliente.equipos.all()

            qs = qs.filter(
                equipo__activo=True, equipo__marca__activo=True
            ).select_related('equipo', 'cliente').distinct()
            
            serializer = EquipoClienteSerializer(qs, many=True)
            return Response(serializer.data)

        if request.method == 'POST':
            # Crear equipos del cliente
            cliente = self.get_object()
            equipo_id = int(request.data['equipoId'])
            cliente.equipos.create(
                equipo_id=equipo_id,
                contador_uso=request.data['contadorUso'],
                alias=request.data.get('alias', '')
            )
            segmentos = [
                {"texto": "Asignó "},
                {"texto": f"el equipo #{equipo_id}", "tipo": "equipo", "id": equipo_id},
                {"texto": f" al {cliente} — "},
                {"texto": str(cliente), "tipo": "cliente", "id": cliente.pk},
            ]
            RegistroActividad.objects.create(
                usuario=request.user, accion='create',
                descripcion=f'Asignó el equipo #{equipo_id} al {cliente}',
                segmentos=segmentos,
            )
            return Response({'success': True}, status=201)

        if request.method == 'DELETE':
            cliente = self.get_object()
            equipo_id = request.data.get('equipoId')

            if not equipo_id:
                return Response(
                    {'detail': 'equipoId es requerido.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                equipo_cliente = cliente.equipos.get(equipo_id=equipo_id)
            except EquipoCliente.DoesNotExist:
                return Response(
                    {'detail': 'El cliente no tiene este equipo asignado.'},
                    status=status.HTTP_404_NOT_FOUND,
                )

            equipo_id = int(equipo_id)
            equipo_cliente.delete()
            segmentos = [
                {"texto": "Desasignó "},
                {"texto": f"el equipo #{equipo_id}", "tipo": "equipo", "id": equipo_id},
                {"texto": f" del {cliente} — "},
                {"texto": str(cliente), "tipo": "cliente", "id": cliente.pk},
            ]
            RegistroActividad.objects.create(
                usuario=request.user, accion='delete',
                descripcion=f'Desasignó el equipo #{equipo_id} del {cliente}',
                segmentos=segmentos,
            )
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=405)

    @action(detail=True, methods=['post'])
    def incrementar_contador(self, request, pk=None):
        cliente = self.get_object()
        equipo_id = request.data.get('equipoId')
        cantidad = request.data.get('cantidad')

        if not equipo_id or not cantidad:
            return Response(
                {'detail': 'equipoId y cantidad son requeridos.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            cantidad = int(cantidad)
        except (TypeError, ValueError):
            return Response(
                {'detail': 'cantidad debe ser un número entero.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if cantidad <= 0:
            return Response(
                {'detail': 'cantidad debe ser un número positivo.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            equipo_cliente = cliente.equipos.select_related('equipo').get(equipo_id=equipo_id)
        except EquipoCliente.DoesNotExist:
            return Response(
                {'detail': 'El cliente no tiene este equipo asignado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        equipo_cliente.contador_uso = F('contador_uso') + cantidad
        equipo_cliente.save(update_fields=['contador_uso'])
        equipo_cliente.refresh_from_db()

        return Response({'contador_uso': equipo_cliente.contador_uso})


class UserViewSet(ActivityLogMixin, viewsets.ModelViewSet):
    queryset = User.objects.filter(is_active=True).select_related('profile')
    serializer_class = UserSerializer

    def get_log_description(self, instance, action):
        segmentos = [
            {"texto": f"{self.verbs[action]} el usuario "},
            {"texto": str(instance), "tipo": "usuario", "id": instance.pk},
        ]
        return f"{self.verbs[action]} el usuario {instance}", segmentos


class SucursalViewSet(viewsets.ModelViewSet):
    queryset = Sucursal.objects.filter(activo=True)
    serializer_class = SucursalSerializer
    permission_classes = []

    @method_decorator(cache_page(60 * 60 * 2))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
