from drf_writable_nested import WritableNestedModelSerializer
from rest_framework.serializers import ModelSerializer

from .models import *


class VentaDetalladoSerializer(ModelSerializer):
    class Meta:
        model = VentaDetallado
        fields = ['cantidad', 'precio', 'descuento', 'especificaciones', 'duplex', 'producto']


class VentaSerializer(WritableNestedModelSerializer):
    detalles = VentaDetalladoSerializer(many=True, required=False)
    
    class Meta:
        model = Venta
        fields = '__all__'
