from django.db.models import Max
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .models import *
from .serializers import *
from utils.mixins import GetWithOrmMixin


class ClienteViewSet(GetWithOrmMixin, ModelViewSet):
    queryset = (
        Cliente.objects.filter(is_active=True)
        .annotate(ultima_venta=Max("ventas__fecha_hora_creacion"))
        .order_by("id")
    )
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]

    orm_fields = [
        'id',
        'nombre',
        'telefono',
        'correo',
        'direccion',
        'rfc',
        'ultima_venta',
        'cliente_especial',
        'descuentos'
    ]
