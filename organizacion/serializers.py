from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Cliente, PerfilUsuario, Sucursal


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'


class SucursalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sucursal
        fields = '__all__'


class PerfilUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilUsuario
        fields = ['rol', 'avatar', 'telefono']


class UserSerializer(serializers.ModelSerializer):
    profile = PerfilUsuarioSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile', 'full_name']

    def get_full_name(self, obj: User):
        return obj.get_full_name()
