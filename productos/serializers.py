from rest_framework import serializers

from .models import Producto, Categoría, Marca, Proveedor, Equipo, Lote, Unidad

__all__ = [
    'CategoriaSerializer',
    'MarcaSerializer',
    'EquipoSerializer',
    'ProveedorSerializer',
    'ProductoSerializer',
    'LoteSerializer',
    'UnidadSerializer',
]


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoría
        fields = '__all__'
        read_only_fields = ['id',]


class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = '__all__'
        read_only_fields = ['id',]


class EquipoSerializer(serializers.ModelSerializer):
    marca = MarcaSerializer(read_only=True)

    def create(self, validated_data):
        marca_id = self.initial_data.get('marca', None)
        try:
            return Equipo.objects.create(
                marca_id=marca_id,
                **validated_data
            )
        except Exception as e:
            raise serializers.ValidationError(f'Error al crear el equipo: {str(e)}')

    class Meta:
        model = Equipo
        fields = '__all__'
        read_only_fields = ['id',]


class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = '__all__'
        read_only_fields = ['id',]


class ProductoSerializer(serializers.ModelSerializer):
    cantidad_disponible = serializers.SerializerMethodField('get_cantidad_disponible')
    categoria = CategoriaSerializer(read_only=True)
    equipo = EquipoSerializer(read_only=True)
    proveedor = ProveedorSerializer(read_only=True)

    def create(self, validated_data):
        categoria_id = self.initial_data.get('categoria', None)
        equipo_id = self.initial_data.get('equipo', None)
        proveedor_id = self.initial_data.get('proveedor', None)

        try:
            return Producto.objects.create(
                categoria_id=categoria_id,
                equipo_id=equipo_id,
                proveedor_id=proveedor_id,
                **validated_data
            )
        except Exception as e:
            raise serializers.ValidationError(f'Error al crear el producto: {str(e)}')
    
    def get_cantidad_disponible(self, instance: Producto):
      return instance.lotes.count()
    
    class Meta:
        model = Producto
        fields = '__all__'
        read_only_fields = ['id', 'creado', 'actualizado']


class LoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lote
        fields = '__all__'
        read_only_fields = ['id', 'creado', 'actualizado']


class UnidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unidad
        fields = '__all__'
        read_only_fields = ['id', 'actualizado']
