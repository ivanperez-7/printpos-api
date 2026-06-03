from django.contrib.auth.models import User
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers
from shapeless_serializers.serializers import InlineShapelessModelSerializer

from .models import Movimiento, MovimientoItem, DetalleEntrada, DetalleSalida
from organizacion.models import Cliente, EquipoCliente
from organizacion.serializers import UserSerializer
from productos.models import Lote, Producto


class MovimientoItemSerializer(serializers.ModelSerializer):
    producto = InlineShapelessModelSerializer(
        model=Producto, fields=['id', 'codigo_interno', 'descripcion'], read_only=True
    )
    producto_id = serializers.PrimaryKeyRelatedField(
        queryset=Producto.objects.all().select_related('categoria', 'proveedor'),
        write_only=True,
        source='producto'
    )
    lote = InlineShapelessModelSerializer(
        model=Lote, fields=['id', 'codigo_lote', 'fecha_entrada'], read_only=True
    )
    lote_id = serializers.PrimaryKeyRelatedField(
        queryset=Lote.objects.all().select_related('producto'),
        write_only=True,
        required=False,
        source='lote'
    )
    equipo_cliente = InlineShapelessModelSerializer(
        model=EquipoCliente, fields=['id', 'alias', 'contador_uso'], read_only=True
    )
    equipo_cliente_id = serializers.PrimaryKeyRelatedField(
        queryset=EquipoCliente.objects.all(),
        write_only=True,
        required=False,
        source='equipo_cliente'
    )

    class Meta:
        model = MovimientoItem
        fields = '__all__'
        read_only_fields = ['id', 'movimiento']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and hasattr(request, 'branch_id'):
            self.fields['equipo_cliente_id'].queryset = EquipoCliente.objects.filter(
                cliente__sucursal=request.branch_id
            )


class DetalleEntradaSerializer(serializers.ModelSerializer):
    recibido_por = UserSerializer(read_only=True)
    recibido_por_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='recibido_por'
    )

    class Meta:
        model = DetalleEntrada
        fields = '__all__'
        read_only_fields = ['id', 'movimiento']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and hasattr(request, 'branch_id'):
            self.fields['recibido_por_id'].queryset = User.objects.filter(
                profile__sucursales=request.branch_id
            )


class DetalleSalidaSerializer(serializers.ModelSerializer):
    cliente = InlineShapelessModelSerializer(model=Cliente, fields=['id', 'nombre'], read_only=True)
    cliente_id = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.all().select_related('sucursal'),
        write_only=True,
        source='cliente'
    )
    
    class Meta:
        model = DetalleSalida
        fields = '__all__'
        read_only_fields = ['id', 'movimiento']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and hasattr(request, 'branch_id'):
            self.fields['cliente_id'].queryset = Cliente.objects.filter(
                sucursal=request.branch_id
            )


class MovimientoSerializer(WritableNestedModelSerializer):
    creado_por = UserSerializer(read_only=True)
    user_aprueba = UserSerializer(read_only=True)
    items = MovimientoItemSerializer(many=True)
    detalle_entrada = DetalleEntradaSerializer(required=False, allow_null=True)
    detalle_salida = DetalleSalidaSerializer(required=False, allow_null=True)

    class Meta:
        model = Movimiento
        fields = '__all__'
        read_only_fields = ['id', 'creado', 'creado_por', 'sucursal']

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError('No se recibieron items para el movimiento.')
        return value
    
    def validate(self, data):
        tipo = data.get('tipo')

        if tipo == 'entrada':
            if not data.get('detalle_entrada'):
                raise serializers.ValidationError('El detalle de entrada es requerido para movimientos de tipo entrada.')
            data.pop('detalle_salida', None)

        if tipo == 'salida':
            if not data.get('detalle_salida'):
                raise serializers.ValidationError('El detalle de salida es requerido para movimientos de tipo salida.')
            data.pop('detalle_entrada', None)

            # Chequeo de disponibilidad de unidades para cada item
            for item in data['items']:
                count = item['lote'].unidades.filter(status='disponible').count()
                if count < item['cantidad']:
                    raise serializers.ValidationError(
                        f'No hay suficientes unidades disponibles ({count}) en el lote {item["lote"].codigo_lote} para la salida.'
                    )

        data['creado_por'] = self.context['request'].user
        data['sucursal_id'] = self.context['request'].branch_id
        return data
