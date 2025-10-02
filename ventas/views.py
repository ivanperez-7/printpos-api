from django.db.models import F
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Venta


@api_view()
@permission_classes([IsAuthenticated])
def get_usuario_pendientes(request):
    count = (
        Venta.objects.filter(vendedor=request.user, estado__icontains='Recibido')
        .exclude(fecha_hora_creacion=F('fecha_hora_entrega'))
        .count()
    )
    return Response(data={'count': count}, status=200)
