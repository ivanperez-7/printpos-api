from django.db.models import F
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Venta
from .serializers import VentaSerializer
from utils.mixins import GetWithOrmMixin


class VentaViewSet(GetWithOrmMixin, ModelViewSet):
    queryset = Venta.objects.all()
    serializer_class = VentaSerializer
    permission_classes = [IsAuthenticated]

    orm_fields = [
        'id',
        'cliente',
        'cliente__nombre',
        'vendedor',
        'vendedor__username',
        'fecha_hora_creacion',
        'fecha_hora_entrega',
        'comentarios',
        'estado',
        'is_active'
    ]
    
    def create(self, request, *args, **kwargs):
        exists = Venta.objects.filter(vendedor=request.user, is_active=True).first()
        if request.data.get('is_active', False) and exists:
            return Response(data=VentaSerializer(exists).data, status=200)
        
        request.data['vendedor'] = request.user.id
        return super().create(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def finalizar(self, request, pk=None):
        venta = self.get_object()
        if not venta.estado == 'No terminada' and not 'Recibido' in venta.estado:
            return Response(data={'detail': 'La venta no está pendiente o sin terminar.'}, status=400)
        
        venta.estado = 'Terminada'
        venta.save()
        return Response(data=VentaSerializer(venta).data, status=200)


@api_view()
@permission_classes([IsAuthenticated])
def get_usuario_pendientes(request):
    count = (
        Venta.objects.filter(vendedor=request.user, estado__icontains='Recibido')
        .exclude(fecha_hora_creacion=F('fecha_hora_entrega'))
        .count()
    )
    return Response(data={'count': count}, status=200)
