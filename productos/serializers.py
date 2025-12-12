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
    marca_id = serializers.PrimaryKeyRelatedField(
        queryset=Marca.objects.all(),
        write_only=True,
        source='marca'
    )

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
    cantidad_disponible = serializers.SerializerMethodField()
    categoria = CategoriaSerializer(read_only=True)
    equipos = EquipoSerializer(read_only=True, many=True)
    proveedor = ProveedorSerializer(read_only=True)

    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=Categoría.objects.all(),
        write_only=True,
        source='categoria'
    )
    equipos_id = serializers.PrimaryKeyRelatedField(
        queryset=Equipo.objects.all(),
        write_only=True,
        many=True,
        source='equipos'
    )
    proveedor_id = serializers.PrimaryKeyRelatedField(
        queryset=Proveedor.objects.all(),
        write_only=True,
        source='proveedor',
        allow_null=True
    )

    class Meta:
        model = Producto
        fields = '__all__'
        read_only_fields = ['id', 'creado', 'actualizado']

    def get_cantidad_disponible(self, instance: Producto):
        return instance.cantidad_disponible


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
