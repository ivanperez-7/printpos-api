from rest_framework.serializers import ModelSerializer
from drf_writable_nested import UniqueFieldsMixin

from .models import *
from utils.serializers import CustomWritableNestedModelSerializer


class ProductoUtilizaInventarioSerializer(ModelSerializer):
    class Meta:
        model = ProductoUtilizaInventario
        fields = ['inventario', 'utiliza_inventario']


class InventarioTieneProductosSerializer(ModelSerializer):
    class Meta:
        model = ProductoUtilizaInventario
        fields = ['producto', 'utiliza_inventario']


class ProductoIntervaloSerializer(UniqueFieldsMixin, ModelSerializer):
    class Meta:
        model = ProductoIntervalo
        fields = ['desde', 'precio_con_iva', 'duplex']


class ProductoGranFormatoSerializer(ModelSerializer):
    class Meta:
        model = ProductoGranFormato
        fields = ['min_m2', 'precio_m2']


class ProductoSerializer(CustomWritableNestedModelSerializer):
    intervalos = ProductoIntervaloSerializer(many=True, required=False, allow_null=True)
    gran_formato = ProductoGranFormatoSerializer(many=False, required=False, allow_null=True)
    inventarios = ProductoUtilizaInventarioSerializer(many=True, required=False, allow_null=True)

    class Meta:
        model = Producto
        fields = '__all__'


class InventarioSerializer(CustomWritableNestedModelSerializer):
    productos = InventarioTieneProductosSerializer(many=True, required=False)

    class Meta:
        model = Inventario
        fields = '__all__'
