from django.db.models import Prefetch
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Movimiento, MovimientoItem
from .serializers import MovimientoSerializer


class MovimientoViewSet(viewsets.ModelViewSet):
    queryset = Movimiento.objects.all().select_related(
        'creado_por__profile', 'user_aprueba__profile',
        'detalle_entrada__recibido_por__profile',
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

    def get_queryset(self):
        queryset = super().get_queryset()
        fecha_inicio = self.request.query_params.get('fechaInicio')
        fecha_fin = self.request.query_params.get('fechaFin')

        if fecha_inicio:
            queryset = queryset.filter(creado__date__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(creado__date__lte=fecha_fin)

        return queryset

    @action(detail=True, methods=['post'])
    def aprobar(self, request, pk=None):
        try:
            movimiento = self.get_object()
            movimiento.approve(request.user)
            return Response({'status': 'aprobado'})
        except Exception as e:
            return Response({'detail': str(e)}, status=500)
    
    @action(detail=False, methods=['get'])
    def get_oldest(self, request):
        return Response(Movimiento.objects.order_by('id').first().creado.date())
