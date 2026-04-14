from rest_framework import serializers

from .models import ConfiguracionSistema


class ConfiguracionSistemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracionSistema
        fields = '__all__'
        read_only_fields = ['id',]
