from rest_framework.serializers import ModelSerializer

from .models import *


class VentaSerializer(ModelSerializer):
    class Meta:
        model = Venta
        fields = '__all__'
