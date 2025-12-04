from rest_framework import serializers

from .models import EntradaInventario, SalidaInventario, EntradaItem, SalidaItem
from organizacion.serializers import UserSerializer


class EntradaItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntradaItem
        fields = ['id', 'cantidad', 'producto']
        read_only_fields = ['id']


class SalidaItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalidaItem
        fields = ['id', 'cantidad', 'producto']
        read_only_fields = ['id']


class EntradaInventarioSerializer(serializers.ModelSerializer):
    recibido_por = UserSerializer(read_only=True)
    user_aprueba = UserSerializer(read_only=True)
    items = EntradaItemSerializer(read_only=True, many=True)

    def create(self, validated_data):
        recibido_por_id = self.initial_data.get('recibido_por', None)
        user_aprueba_id = self.initial_data.get('user_aprueba', None)
        
        try:
            return EntradaInventario.objects.create(
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
    entregado_por = UserSerializer(read_only=True)
    user_aprueba = UserSerializer(read_only=True)
    items = SalidaItemSerializer(read_only=True, many=True)

    def create(self, validated_data):
        entregado_por_id = self.initial_data.get('entregado_por', None)
        user_aprueba_id = self.initial_data.get('user_aprueba', None)
        try:
            return SalidaInventario.objects.create(
                entregado_por_id=entregado_por_id,
                user_aprueba_id=user_aprueba_id,
                **validated_data
            )
        except Exception as e:
            raise serializers.ValidationError(f'Error al crear la salida de inventario: {str(e)}')
    
    class Meta:
        model = SalidaInventario
        fields = '__all__'
        read_only_fields = ['id', 'creado']
