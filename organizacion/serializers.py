from django.contrib.auth.models import User
from rest_framework import serializers

from .models import PerfilUsuario, Sucursal


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
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']
