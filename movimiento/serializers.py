from rest_framework import serializers

from .models import EntradaInventario, SalidaInventario
from productos.serializers import ProductoSerializer


class EntradaInventarioSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer(read_only=True)

    def create(self, validated_data):
        producto_id = self.initial_data.get('producto', None)
        try:
            return EntradaInventario.objects.create(
                producto_id=producto_id,
                **validated_data
            )
        except Exception as e:
            raise serializers.ValidationError(f'Error al crear la entrada de inventario: {str(e)}')

    class Meta:
        model = EntradaInventario
        fields = '__all__'
        read_only_fields = ['id', 'creado']


class SalidaInventarioSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer(read_only=True)

    def create(self, validated_data):
        producto_id = self.initial_data.get('producto', None)
        try:
            return SalidaInventario.objects.create(
                producto_id=producto_id,
                **validated_data
            )
        except Exception as e:
            raise serializers.ValidationError(f'Error al crear la salida de inventario: {str(e)}')
    
    class Meta:
        model = SalidaInventario
        fields = '__all__'
        read_only_fields = ['id', 'creado']
