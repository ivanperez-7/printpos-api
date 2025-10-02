from rest_framework.serializers import ModelSerializer

from .models import *


class CajaSerializer(ModelSerializer):
    class Meta:
        model = Caja
        fields = '__all__'
