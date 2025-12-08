from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Movimiento
from .serializers import MovimientoSerializer


class MovimientoViewSet(viewsets.ModelViewSet):
    queryset = Movimiento.objects.all().select_related(
        'creado_por', 'user_aprueba',
        'detalle_entrada__recibido_por',
        'detalle_salida__cliente'
    ).prefetch_related('items', 'items__producto')
    
    serializer_class = MovimientoSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['items__producto']

    @action(detail=True, methods=['post'])
    def aprobar(self, request, pk=None):
        movimiento = self.get_object()
        movimiento.approve(request.user)
        return Response({"status": "aprobado"})
