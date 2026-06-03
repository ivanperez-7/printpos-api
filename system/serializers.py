from rest_framework import serializers
from shapeless_serializers.serializers import InlineShapelessModelSerializer

from .models import AlertaInventario, ConfiguracionSistema, RegistroActividad
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


class RegistroActividadSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)
    sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)

    class Meta:
        model = RegistroActividad
        fields = ['id', 'usuario', 'usuario_nombre', 'accion', 'descripcion', 'segmentos', 'sucursal', 'sucursal_nombre', 'creado']
        read_only_fields = fields
