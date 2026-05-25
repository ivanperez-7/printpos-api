from rest_framework import serializers
from shapeless_serializers.serializers import InlineShapelessModelSerializer

from .models import AlertaInventario, ConfiguracionSistema
from productos.models import Producto


class ConfiguracionSistemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracionSistema
        fields = '__all__'
        read_only_fields = ['id',]


class AlertaInventarioSerializer(serializers.ModelSerializer):
    producto = InlineShapelessModelSerializer(
        model=Producto, fields=['id', 'codigo_interno', 'descripcion'], read_only=True
    )

    class Meta:
        model = AlertaInventario
        fields = ['id', 'producto', 'tipo_alerta', 'mensaje', 'creado', 'resuelto']
        read_only_fields = ['id', 'producto', 'tipo_alerta', 'mensaje', 'creado']
