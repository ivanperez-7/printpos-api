from django.db.models import Count, Q, F
from django.db.models.functions import TruncDate
from django.utils import timezone
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Producto, Categoría, Marca, Proveedor, Equipo, Lote, Unidad
from .serializers import *
from movimiento.models import Movimiento
from organizacion.views import ClienteViewSet

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
    queryset = (
        Producto.objects.exclude(status='inactivo')
        .select_related('categoria', 'proveedor')
        .prefetch_related('equipos')
    )
    serializer_class = ProductoSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['sku']


class LoteViewSet(viewsets.ModelViewSet):
    queryset = Lote.objects.exclude(producto__status='inactivo').select_related('producto')
    serializer_class = LoteSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['producto']


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
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer


@api_view()
def dashboard_view(request):
    productos = ProductoViewSet.queryset.all()
    lotes = LoteViewSet.queryset.all()
    categorias = CategoriaViewSet.queryset.all()
    proveedores = ProveedorViewSet.queryset.all()
    clientes = ClienteViewSet.queryset.all()

    hace_30_dias = timezone.now() - timezone.timedelta(days=30)

    return Response(
        {
            'stats': {
                'productos': productos.count(),
                'lotes': lotes.count(),
                'categorias': categorias.count(),
                'proveedores': proveedores.count(),
                'clientes': clientes.count(),
            },
            'categoriasChart': (
                categorias.annotate(
                    cantidad=Count('producto', filter=Q(producto__status='activo'))
                )
                .filter(cantidad__gt=0)
                .values('nombre', 'cantidad')
            ),
            'entradasChart': (
                Movimiento.objects.filter(tipo='entrada', creado__gte=hace_30_dias)
                .annotate(fecha_creado=TruncDate('creado'))
                .values('fecha_creado')
                .annotate(total=Count('id'))
            ),
            'clientesChart': [{"tipo": "lol", "cantidad": 120}, {"tipo": "lol2", "cantidad": 57}],
            'productosBajos': (
                productos.annotate(
                    stock=Count('lotes__unidades', filter=Q(lotes__unidades__status='disponible'))
                )
                .filter(stock__lte=F('min_stock'))
                .order_by('stock')
                .values('descripcion', 'categoria__nombre', 'stock')
            ),
        }
    )
