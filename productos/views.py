from django.db.models import Count, Q, F
from django.utils import timezone
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Categoría, Marca, Proveedor, Equipo, Unidad
from .serializers import *
from movimiento.models import Movimiento
from organizacion.queries import clientes_queryset
from productos.queries import lotes_queryset, productos_queryset

__all__ = [
    'ProductoViewSet',
    'LoteViewSet',
    'UnidadViewSet',
    'CategoriaViewSet',
    'MarcaViewSet',
    'EquipoViewSet',
    'ProveedorViewSet',
    'dashboard_view',
]


class ProductoViewSet(viewsets.ModelViewSet):
    serializer_class = ProductoSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['sku', 'categoria', 'equipos__marca', 'equipos']

    def get_queryset(self):
        return productos_queryset()


class LoteViewSet(viewsets.ModelViewSet):
    serializer_class = LoteSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['producto', 'codigo_lote']

    def get_queryset(self):
        return lotes_queryset()


class UnidadViewSet(viewsets.ModelViewSet):
    queryset = Unidad.objects.exclude(lote__producto__status='inactivo').select_related('lote')
    serializer_class = UnidadSerializer


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoría.objects.all()
    serializer_class = CategoriaSerializer


class MarcaViewSet(viewsets.ModelViewSet):
    queryset = Marca.objects.filter(activo=True)
    serializer_class = MarcaSerializer


class EquipoViewSet(viewsets.ModelViewSet):
    queryset = (
        Equipo.objects.filter(activo=True, marca__activo=True)
        .order_by('marca__nombre', 'nombre')
        .select_related('marca')
    )
    serializer_class = EquipoSerializer


class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.filter(activo=True)
    serializer_class = ProveedorSerializer


@api_view()
def dashboard_view(request):
    productos = productos_queryset()
    categorias = Categoría.objects.all()

    hace_30_dias = (timezone.now() - timezone.timedelta(days=30)).date()

    movs_filter = Q(movimientoitem__movimiento__creado__date__gte=hace_30_dias, movimientoitem__movimiento__aprobado=True)

    return Response(
        {
            'stats': {
                'productos': productos.count(),
                'lotes': lotes_queryset().filter(cantidad_restante__gt=0).count(),
                'categorias': categorias.count(),
                'proveedores': Proveedor.objects.filter(activo=True).count(),
                'clientes': clientes_queryset(request.branch_id).count(),
            },
            'categoriasChart': (
                categorias.values('nombre').annotate(
                    cantidad=Count('producto', filter=Q(producto__status='activo'))
                )
                .filter(cantidad__gt=0)
            ),
            'movimientosChart': (
                Movimiento.objects.filter(creado__date__gte=hace_30_dias, aprobado=True)
                .values(fecha_creado=F('creado__date'))
                .annotate(
                    entradas=Count('id', filter=Q(tipo='entrada')),
                    salidas=Count('id', filter=Q(tipo='salida'))
                )
            ),
            'topProductosChart': (
                productos.values('id', 'codigo_interno')
                .annotate(
                    total_movimientos=Count('movimientoitem__movimiento', distinct=True, filter=movs_filter)
                )
                .filter(total_movimientos__gt=0)
                .order_by('-total_movimientos')[:10]
            ),
            'productosBajos': (
                productos.filter(cantidad_disponible__lt=F('min_stock'))
                .order_by('-cantidad_disponible')
                .values('id', 'descripcion', 'categoria__nombre', 'cantidad_disponible', 'min_stock')
            ),
        }
    )
