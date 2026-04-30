from django.db.models import Prefetch
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Movimiento, MovimientoItem
from .serializers import MovimientoSerializer


class MovimientoViewSet(viewsets.ModelViewSet):
    queryset = Movimiento.objects.all().select_related(
        'creado_por', 'user_aprueba',
        'creado_por__profile', 'user_aprueba__profile',
        'detalle_entrada__recibido_por', 'detalle_entrada__recibido_por__profile',
        'detalle_salida__cliente'
    ).prefetch_related(
        Prefetch(
            'items',
            queryset=MovimientoItem.objects.select_related('producto', 'lote')
        )
    ).distinct()
    
    serializer_class = MovimientoSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['items__producto', 'detalle_salida__cliente']

    @action(detail=True, methods=['post'])
    def aprobar(self, request, pk=None):
        try:
            movimiento = self.get_object()
            movimiento.approve(request.user)
            return Response({'status': 'aprobado'})
        except Exception as e:
            return Response({'detail': str(e)}, status=500)
