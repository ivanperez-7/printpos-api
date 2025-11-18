from rest_framework import serializers

from .models import EntradaInventario, SalidaInventario
from productos.serializers import ProductoSerializer, ProveedorSerializer
from organizacion.serializers import UserSerializer


class EntradaInventarioSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer(read_only=True)
    proveedor = ProveedorSerializer(read_only=True)
    recibido_por = UserSerializer(read_only=True)
    user_aprueba = UserSerializer(read_only=True)

    def create(self, validated_data):
        producto_id = self.initial_data.get('producto', None)
        proveedor_id = self.initial_data.get('proveedor', None)
        recibido_por_id = self.initial_data.get('recibido_por', None)
        user_aprueba_id = self.initial_data.get('user_aprueba', None)
        
        try:
            return EntradaInventario.objects.create(
                producto_id=producto_id,
                proveedor_id=proveedor_id,
                recibido_por_id=recibido_por_id,
                user_aprueba_id=user_aprueba_id,
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
