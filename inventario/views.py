from decimal import Decimal

from django.db.models import Case, CharField, DecimalField, F, Sum, Value, When
from django.db.models.functions import Cast, Coalesce, Concat, Round
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
                precio_con_iva=Coalesce('intervalos__precio_con_iva', 'gran_formato__precio_m2'),
                costo_prod=Sum(F('inventarios__utiliza_inventario') * F('inventarios__inventario__precio_lote') / F('inventarios__inventario__tamano_lote'), output_field=DecimalField())
            )
            .annotate(
                descripcion_=Concat(
                    'descripcion',
                    Case(When(intervalos__desde__gt=1, then=Concat(Value(', desde '), Cast('intervalos__desde', CharField()), Value(' unidades')))),
                    Case(When(intervalos__duplex=True, then=Value(' [PRECIO DUPLEX]')))
                ),
                precio_sin_iva=Round(F('precio_con_iva') / Decimal('1.16'), 2),
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

        if producto.categoria == 'S':
            cantidad = request.data.get('cantidad', 1)
            duplex = request.data.get('duplex', False)
            try:
                precio_con_iva, importe = producto.obtener_precio_importe_simple(cantidad, descuento_unit, duplex)
            except ValueError as e:
                return Response(data={'error': str(e)}, status=400)
            return Response(data={'precio_con_iva': precio_con_iva, 'importe': importe}, status=200)
        
        # === Producto de gran formato ===
        ancho_producto = request.data.get('ancho_producto')
        alto_producto = request.data.get('alto_producto')
        if ancho_producto is None or alto_producto is None:
            return Response(data={'error': 'Para productos de gran formato se requieren los campos "ancho_producto" y "alto_producto".'}, status=400)
        
        ancho_material = request.data.get('ancho_material')
        if ancho_material is None:
            return Response(data={'error': 'Para productos de gran formato se requiere el campo "ancho_material".'}, status=400)
        
        # Si el alto del producto sobrepasa el ancho del material, quiere decir
        # que no se pudo imprimir de forma normal, por lo tanto, cobrar sobrante.
        if alto_producto > ancho_material:
            ancho_producto = ancho_material

        try:
            precio_con_iva, importe = producto.obtener_precio_importe_gran_formato(ancho_producto*alto_producto, descuento_unit)
        except ValueError as e:
            return Response(data={'error': str(e)}, status=400)

        return Response(data={'precio_con_iva': precio_con_iva, 'importe': importe}, status=200)


class InventarioViewSet(GetWithOrmMixin, ModelViewSet):
    queryset = Inventario.objects.filter(is_active=True)
    serializer_class = InventarioSerializer
    permission_classes = [IsAuthenticated]

    orm_fields = ['id', 'nombre']
