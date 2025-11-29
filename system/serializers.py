from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import ConfiguracionSistema


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super(CustomTokenObtainPairSerializer, self).validate(attrs)
        user = User.objects.get(username=attrs['username'])
        try:
            avatar = user.profile.avatar.path
        except:
            avatar = None
        
        return {
            'access': data['access'],
            'refresh': data['refresh'],
            'username': attrs['username'],
            'email': user.email,
            'avatar': avatar,
        }


class ConfiguracionSistemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracionSistema
        fields = '__all__'
        read_only_fields = ['id',]
