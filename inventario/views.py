from django.db.models import Case, CharField, F, Sum, Value, When
from django.db.models.functions import Cast, Coalesce, Concat
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from .models import *
from .serializers import *
from utils.mixins import GetWithOrmMixin


class ProductoViewSet(ModelViewSet):
    queryset = Producto.objects.filter(is_active=True)
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        qs = (
            self.queryset.annotate(
                precio_con_iva=Coalesce(F('intervalos__precio_con_iva'), F('gran_formato__precio_m2')),
                costo_prod=Sum(F('inventarios__utiliza_inventario') * F('inventarios__inventario__precio_lote') / F('inventarios__inventario__tamano_lote'))
            )
            .annotate(
                descripcion_=Concat(
                    F("descripcion"),
                    Case(When(intervalos__desde__gt=1, then=Concat(Value(', desde '), Cast(F('intervalos__desde'), CharField()), Value(' unidades')))),
                    Case(When(intervalos__duplex=True, then=Value(' [PRECIO DUPLEX]')))
                ),
                precio_sin_iva=F('precio_con_iva') / 1.16,
                utilidad=F('precio_con_iva') - F('costo_prod')
            )
            .order_by('pk', 'intervalos__desde', 'intervalos__duplex')
            .values('id', 'codigo', 'descripcion_', 'abreviado', 'categoria', 'precio_con_iva', 'precio_sin_iva', 'costo_prod', 'utilidad')
        )
        return Response(data=qs, status=200)
    
    @action(detail=True, methods=['post'])
    def get_precio_importe(self, request, pk=None):
        producto = self.get_object()
        descuento_unit = request.data.get('descuento_unit', 0.0)
        cantidad = request.data.get('cantidad', 1)
        
        intervalos = producto.intervalos.filter(desde__lte=cantidad).order_by('-desde', '-duplex')
        if not request.data.get('duplex', False):
            intervalos = intervalos.exclude(duplex=True)
        
        if intervalo := intervalos.first():
            # Usar precio de intervalo
            precio_con_iva = intervalo.precio_con_iva
        else:
            # Usar precio de gran formato
            cantidad = max(producto.gran_formato.min_m2, cantidad)
            precio_con_iva = producto.gran_formato.precio_m2
        return Response(data={'precio_con_iva': precio_con_iva, 'importe': (precio_con_iva - descuento_unit) * cantidad}, status=200)


class InventarioViewSet(GetWithOrmMixin, ModelViewSet):
    queryset = Inventario.objects.filter(is_active=True)
    serializer_class = InventarioSerializer
    permission_classes = [IsAuthenticated]

    orm_fields = ['id', 'nombre']
