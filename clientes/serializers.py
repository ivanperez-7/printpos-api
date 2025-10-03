from rest_framework.serializers import ModelSerializer

from .models import *


class ClienteSerializer(ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'
