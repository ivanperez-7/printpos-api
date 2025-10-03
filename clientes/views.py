from django.db.models import Max
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import *


@api_view()
@permission_classes([IsAuthenticated])
def get_tabla_clientes(request):
    clientes = (
        Cliente.objects
        .exclude(ventas__estado__in=["Cancelada", "No terminada"], is_active=False)
        .annotate(ultima_venta=Max("ventas__fecha_hora_creacion"))
        .order_by("id")
        .values("id", "nombre", "telefono", "correo", "direccion", "rfc", "ultima_venta")
    )
    return Response(data=clientes, status=200)
