from datetime import date

from django.db.models import Prefetch
from django.http import HttpResponse
from django_filters import rest_framework as filters
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Movimiento, MovimientoItem
from .serializers import MovimientoSerializer
from productos.models import Lote
from system.models import RegistroActividad
from utils.mixins import ActivityLogMixin
from utils.pdf_barcodes import generate_lot_labels_pdf


class MovimientoViewSet(ActivityLogMixin, viewsets.ModelViewSet):
    queryset = Movimiento.objects.all().select_related(
        'creado_por__profile', 'user_aprueba__profile',
        'detalle_entrada__recibido_por__profile',
        'detalle_salida__cliente'
    ).prefetch_related(
        Prefetch(
            'items',
            queryset=MovimientoItem.objects.select_related('producto', 'lote', 'equipo_cliente')
        )
    ).distinct()
    
    serializer_class = MovimientoSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['items__producto', 'detalle_salida__cliente']

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(sucursal=self.request.branch_id)
        fecha_inicio = self.request.query_params.get('fechaInicio')
        fecha_fin = self.request.query_params.get('fechaFin')

        if fecha_inicio:
            queryset = queryset.filter(creado__date__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(creado__date__lte=fecha_fin)

        return queryset

    def get_log_description(self, instance, action):
        # str() ya incluye "Movimiento 42 (entrada)", evitar duplicado
        segmentos = [
            {"texto": f"{self.verbs[action]} el "},
            {"texto": str(instance), "tipo": "movimiento", "id": instance.pk},
        ]
        return f"{self.verbs[action]} el {instance}", segmentos

    @action(detail=True, methods=['post'])
    def aprobar(self, request, pk=None):
        try:
            movimiento = self.get_object()
            movimiento.approve(request.user)
            segmentos = [
                {"texto": "Aprobó el "},
                {"texto": str(movimiento), "tipo": "movimiento", "id": movimiento.pk},
            ]
            RegistroActividad.objects.create(
                usuario=request.user, accion='approve',
                descripcion=f'Aprobó el {movimiento}',
                segmentos=segmentos,
                sucursal_id=request.branch_id,
            )
            return Response({'status': 'aprobado'})
        except PermissionError as e:
            return Response({'detail': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=500)
    
    @action(detail=False, methods=['get'])
    def get_oldest(self, request):
        qs = self.filter_queryset(Movimiento.objects.filter(sucursal=request.branch_id)) # branch scope, sin filtrar por fecha
        oldest = qs.order_by('id').first()
        if oldest:
            return Response({'fecha': oldest.creado.date()})
        return Response({'fecha': date.today()})

    @action(detail=True, methods=['get'])
    def etiquetas(self, request, pk=None):
        movimiento = self.get_object()
        
        if movimiento.tipo != 'entrada':
            return Response({'detail': 'Solo movimientos de entrada tienen etiquetas.'}, status=400)
        if not movimiento.aprobado:
            return Response({'detail': 'El movimiento debe estar aprobado.'}, status=400)

        lotes = Lote.objects.filter(movimientoitem__movimiento=movimiento)
        if not lotes.exists():
            return Response({'detail': 'No se encontraron lotes para este movimiento.'}, status=404)

        pdf_bytes = generate_lot_labels_pdf(lotes)
        return HttpResponse(pdf_bytes, content_type='application/pdf',
                            headers={'Content-Disposition': f'attachment; filename="etiquetas-movimiento-{pk}.pdf"'})
