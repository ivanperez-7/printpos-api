from rest_framework import viewsets

from .models import Producto, Categoría, Marca, Proveedor, Equipo
from .serializers import ProductoSerializer, CategoriaSerializer, MarcaSerializer, ProveedorSerializer, EquipoSerializer


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.exclude(status='inactivo')
    serializer_class = ProductoSerializer


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
