from rest_framework.serializers import ModelSerializer

from .models import *


class VentaDetalladoSerializer(ModelSerializer):
    class Meta:
        model = VentaDetallado
        fields = '__all__'


class VentaSerializer(ModelSerializer):
    detalles = VentaDetalladoSerializer(many=True, required=False)
    
    class Meta:
        model = Venta
        fields = '__all__'
