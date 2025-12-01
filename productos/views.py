from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Producto, Categoría, Marca, Proveedor, Equipo, Lote, Unidad
from .serializers import *

__all__ = [
    'ProductoViewSet',
    'LoteViewSet',
    'UnidadViewSet',
    'CategoriaViewSet',
    'MarcaViewSet',
    'EquipoViewSet',
    'ProveedorViewSet',
]


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.exclude(status='inactivo')
    serializer_class = ProductoSerializer

    @action(detail=True, methods=['get'])
    def lotes(self, request, pk=None):
        try:
            qs = Lote.objects.filter(producto_id=pk)
            serializer = LoteSerializer(qs, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class LoteViewSet(viewsets.ModelViewSet):
    queryset = Lote.objects.exclude(producto__status='inactivo')
    serializer_class = LoteSerializer


class UnidadViewSet(viewsets.ModelViewSet):
    queryset = Unidad.objects.exclude(lote__producto__status='inactivo')
    serializer_class = UnidadSerializer


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoría.objects.all()
    serializer_class = CategoriaSerializer


class MarcaViewSet(viewsets.ModelViewSet):
    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer


class EquipoViewSet(viewsets.ModelViewSet):
    queryset = Equipo.objects.all()
    serializer_class = EquipoSerializer


class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
