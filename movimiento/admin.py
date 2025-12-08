from django.contrib import admin

from .models import Movimiento, MovimientoItem, DetalleEntrada, DetalleSalida


class MovimientoItemInline(admin.TabularInline):
    model = MovimientoItem
    extra = 0
    autocomplete_fields = ['producto']


class DetalleEntradaInline(admin.StackedInline):
    model = DetalleEntrada
    extra = 0
    max_num = 1
    can_delete = False


class DetalleSalidaInline(admin.StackedInline):
    model = DetalleSalida
    extra = 0
    max_num = 1
    can_delete = False


@admin.register(Movimiento)
class MovimientoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'tipo', 'creado', 'creado_por',
        'aprobado', 'aprobado_fecha',
    )

    list_filter = (
        'tipo', 'aprobado', 'creado_por',
        'creado',
    )

    search_fields = (
        'id',
        'comentarios',
        'detalle_entrada__numero_factura',
        'detalle_salida__cliente__nombre',
    )

    readonly_fields = [
        'creado',
        'aprobado',
        'aprobado_fecha',
        'user_aprueba',
    ]

    autocomplete_fields = ['creado_por', 'user_aprueba']

    inlines = [MovimientoItemInline]

    def get_inlines(self, request, obj=None):
        """
        Mostrar solo el inline correspondiente
        según el tipo de movimiento.
        """
        if not obj:
            return []  # al crear no se muestran aún

        if obj.tipo == 'entrada':
            return [DetalleEntradaInline, MovimientoItemInline]

        if obj.tipo == 'salida':
            return [DetalleSalidaInline, MovimientoItemInline]

        return [MovimientoItemInline]


@admin.register(DetalleEntrada)
class DetalleEntradaAdmin(admin.ModelAdmin):
    list_display = ('movimiento', 'numero_factura', 'recibido_por')


@admin.register(DetalleSalida)
class DetalleSalidaAdmin(admin.ModelAdmin):
    list_display = ('movimiento', 'cliente', 'tecnico', 'requiere_aprobacion')
