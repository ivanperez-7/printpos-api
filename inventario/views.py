from django.db.models import Case, CharField, F, Sum, Value, When
from django.db.models.functions import Cast, Coalesce, Concat
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from .models import *
from .serializers import *
from utils.mixins import GetWithOrmMixin


class ProductoViewSet(GetWithOrmMixin, ModelViewSet):
    queryset = Producto.objects.filter(is_active=True)
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated]

    orm_fields = ['codigo', 'descripcion', 'abreviado', 'categoria', 'is_active']

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


class InventarioViewSet(GetWithOrmMixin, ModelViewSet):
    queryset = Inventario.objects.filter(is_active=True)
    serializer_class = InventarioSerializer
    permission_classes = [IsAuthenticated]

    orm_fields = ['id', 'nombre']
