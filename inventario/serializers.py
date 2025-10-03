from rest_framework.serializers import ModelSerializer
from drf_writable_nested import WritableNestedModelSerializer

from .models import *


class ProductoUtilizaInventarioSerializer(ModelSerializer):
    class Meta:
        model = ProductoUtilizaInventario
        fields = ['inventario', 'utiliza_inventario']


class ProductoIntervaloSerializer(ModelSerializer):
    class Meta:
        model = ProductoIntervalo
        fields = ['desde', 'precio_con_iva', 'duplex']


class ProductoGranFormatoSerializer(ModelSerializer):
    class Meta:
        model = ProductoGranFormato
        fields = ['min_m2', 'precio_m2']


class ProductoSerializer(WritableNestedModelSerializer):
    intervalos = ProductoIntervaloSerializer(many=True, required=False)
    gran_formato = ProductoGranFormatoSerializer(many=False, required=False)
    inventarios = ProductoUtilizaInventarioSerializer(many=True, required=False)

    class Meta:
        model = Producto
        fields = '__all__'


class InventarioSerializer(ModelSerializer):
    class Meta:
        model = Inventario
        fields = '__all__'
