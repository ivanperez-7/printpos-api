from rest_framework import serializers

from .models import Producto, Categoría, Marca, Proveedor, Equipo, Lote, Unidad
from organizacion.models import EquipoCliente

__all__ = [
    'CategoriaSerializer',
    'MarcaSerializer',
    'EquipoSerializer',
    'ProveedorSerializer',
    'ProductoSerializer',
    'LoteSerializer',
    'UnidadSerializer',
    'EquipoClienteSerializer',
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
        queryset=Equipo.objects.all().select_related('marca'),
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
        if hasattr(instance, 'cantidad_disponible'):
            return instance.cantidad_disponible
        return Unidad.objects.filter(lote__producto=instance, status='disponible').count()


class LoteSerializer(serializers.ModelSerializer):
    class InlineProductoSerializer(ProductoSerializer):
        class Meta(ProductoSerializer.Meta):
            fields = ['id', 'codigo_interno', 'descripcion', 'equipos']

    cantidad_restante = serializers.SerializerMethodField()
    producto = InlineProductoSerializer(read_only=True)

    class Meta:
        model = Lote
        fields = '__all__'
        read_only_fields = ['id', 'creado', 'actualizado']
    
    def get_cantidad_restante(self, instance: Lote):
        try:
            return instance.cantidad_restante
        except AttributeError:
            return instance.unidades.filter(status='disponible').count()


class UnidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unidad
        fields = '__all__'
        read_only_fields = ['id', 'actualizado']


class EquipoClienteSerializer(serializers.ModelSerializer):
    cliente_id = serializers.IntegerField(source='cliente.id', read_only=True)
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    equipo_id = serializers.IntegerField(source='equipo.id', read_only=True)
    equipo_nombre = serializers.CharField(source='equipo.nombre', read_only=True)
    marca_nombre = serializers.CharField(source='equipo.marca.nombre', read_only=True)

    class Meta:
        model = EquipoCliente
        fields = ['id', 'cliente_id', 'cliente_nombre', 'equipo_id', 'equipo_nombre', 'marca_nombre', 'alias', 'contador_uso']
