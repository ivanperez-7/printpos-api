from rest_framework import serializers

from .models import Producto, Categoría, Marca, Proveedor


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


class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = '__all__'
        read_only_fields = ['id',]


class ProductoSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)
    marca = MarcaSerializer(read_only=True)
    proveedor = ProveedorSerializer(read_only=True)

    def create(self, validated_data):
        categoria_id = self.initial_data.get('categoria', None)
        marca_id = self.initial_data.get('marca', None)
        proveedor_id = self.initial_data.get('proveedor', None)

        try:
            return Producto.objects.create(
                categoria_id=categoria_id,
                marca_id=marca_id,
                proveedor_id=proveedor_id,
                **validated_data
            )
        except Exception as e:
            raise serializers.ValidationError(f'Error al crear el producto: {str(e)}')
    
    class Meta:
        model = Producto
        fields = '__all__'
        read_only_fields = ['id', 'creado', 'actualizado']
