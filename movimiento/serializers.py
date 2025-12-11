from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers
from shapeless_serializers.serializers import InlineShapelessModelSerializer

from .models import Movimiento, MovimientoItem, DetalleEntrada, DetalleSalida
from organizacion.models import Cliente
from productos.models import Producto


class MovimientoItemSerializer(serializers.ModelSerializer):
    producto = InlineShapelessModelSerializer(
        model=Producto, fields=['id', 'codigo_interno', 'descripcion'], read_only=True
    )
    producto_id = serializers.PrimaryKeyRelatedField(
        queryset=Producto.objects.all(),
        write_only=True,
        source='producto'
    )

    class Meta:
        model = MovimientoItem
        fields = '__all__'
        read_only_fields = ['id', 'movimiento']


class DetalleEntradaSerializer(serializers.ModelSerializer):
    recibido_por = InlineShapelessModelSerializer(
        model=User, fields=['username', 'first_name', 'last_name'], read_only=True
    )
    recibido_por_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='recibido_por'
    )

    class Meta:
        model = DetalleEntrada
        fields = '__all__'
        read_only_fields = ['id', 'movimiento']


class DetalleSalidaSerializer(serializers.ModelSerializer):
    cliente = InlineShapelessModelSerializer(model=Cliente, fields=['id', 'nombre'], read_only=True)
    cliente_id = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.all(),
        write_only=True,
        source='cliente'
    )
    
    class Meta:
        model = DetalleSalida
        fields = '__all__'
        read_only_fields = ['id', 'movimiento']


class MovimientoSerializer(serializers.ModelSerializer):
    creado_por = InlineShapelessModelSerializer(
        model=User, fields=['username', 'first_name', 'last_name'], read_only=True
    )
    user_aprueba = InlineShapelessModelSerializer(
        model=User, fields=['username', 'first_name', 'last_name'], read_only=True
    )
    items = MovimientoItemSerializer(many=True)
    detalle_entrada = DetalleEntradaSerializer(required=False)
    detalle_salida = DetalleSalidaSerializer(required=False)

    class Meta:
        model = Movimiento
        fields = '__all__'
        read_only_fields = ['id', 'creado', 'creado_por']

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop("items")
        d_entrada = validated_data.pop("detalle_entrada", None)
        d_salida = validated_data.pop("detalle_salida", None)

        if not items_data:
            raise serializers.ValidationError('No se recibieron items para el movimiento')

        movimiento = Movimiento.objects.create(creado_por=self.context['request'].user, **validated_data)

        for item in items_data:
            MovimientoItem.objects.create(movimiento=movimiento, **item)

        if movimiento.tipo == "entrada":
            DetalleEntrada.objects.create(movimiento=movimiento, **d_entrada)
        elif movimiento.tipo == "salida":
            DetalleSalida.objects.create(movimiento=movimiento, **d_salida)

        return movimiento
