from rest_framework.serializers import ModelSerializer

from .models import *


class ProductoSerializer(ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'


class InventarioSerializer(ModelSerializer):
    class Meta:
        model = Inventario
        fields = '__all__'
