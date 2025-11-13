from django.contrib import admin

from .models import EntradaInventario, SalidaInventario, PasoAprobacion


@admin.register(EntradaInventario)
class EntradaInventarioAdmin(admin.ModelAdmin):
    'Gestión de entradas de inventario.'
    list_display = (
        'creado', 'producto', 'cantidad', 'tipo_entrada', 'proveedor', 'recibido_por', 'aprobado'
    )
    list_filter = ('tipo_entrada', 'aprobado', 'creado')
    search_fields = (
        'producto__internal_code', 'producto__description',
        'proveedor__name', 'numero_factura'
    )
    autocomplete_fields = ('producto', 'proveedor', 'recibido_por')
    readonly_fields = ('creado',)
    list_per_page = 25
    date_hierarchy = 'creado'
    ordering = ('-creado',)

    fieldsets = (
        ('Información principal', {
            'fields': (
                'producto', 'proveedor', 'tipo_entrada', 'numero_factura',
                'cantidad', 'recibido_por', 'comentarios'
            ),
        }),
        ('Estado de aprobación', {
            'fields': ('aprobado',),
        }),
        ('Auditoría', {
            'fields': ('creado',),
        }),
    )

    actions = ['aplicar_a_stock_action']

    def aplicar_a_stock_action(self, request, queryset):
        'Acción para aplicar múltiples entradas al stock.'
        count = 0
        for entrada in queryset:
            entrada.aplicar_a_stock()
            count += 1
        self.message_user(request, f'{count} entradas aplicadas al stock correctamente.')
    aplicar_a_stock_action.short_description = 'Aplicar entradas seleccionadas al stock'


@admin.register(SalidaInventario)
class SalidaInventarioAdmin(admin.ModelAdmin):
    'Gestión de salidas de inventario.'
    list_display = (
        'creado', 'producto', 'cantidad', 'tipo_salida',
        'nombre_cliente', 'tecnico', 'entregado_por', 'aprobado'
    )
    list_filter = ('tipo_salida', 'requiere_aprobacion', 'aprobado', 'creado')
    search_fields = (
        'producto__internal_code', 'producto__description',
        'nombre_cliente', 'tecnico'
    )
    autocomplete_fields = ('producto', 'entregado_por')
    readonly_fields = ('creado',)
    list_per_page = 25
    date_hierarchy = 'creado'
    ordering = ('-creado',)

    fieldsets = (
        ('Información principal', {
            'fields': (
                'producto', 'tipo_salida', 'cantidad',
                'nombre_cliente', 'tecnico', 'equipo_asociado'
            ),
        }),
        ('Responsables', {
            'fields': ('entregado_por', 'recibido_por'),
        }),
        ('Aprobación y comentarios', {
            'fields': ('requiere_aprobacion', 'aprobado', 'comentarios'),
        }),
        ('Auditoría', {
            'fields': ('creado',),
        }),
    )

    actions = ['aplicar_a_stock_action']

    def aplicar_a_stock_action(self, request, queryset):
        'Acción para descontar múltiples salidas del stock.'
        exitosas, errores = 0, 0
        for salida in queryset:
            try:
                salida.aplicar_a_stock()
                exitosas += 1
            except ValueError:
                errores += 1
        msg = f'{exitosas} salidas aplicadas al stock correctamente.'
        if errores:
            msg += f' {errores} no se aplicaron por falta de stock.'
        self.message_user(request, msg)
    aplicar_a_stock_action.short_description = 'Aplicar salidas seleccionadas al stock'


@admin.register(PasoAprobacion)
class PasoAprobacionAdmin(admin.ModelAdmin):
    'Flujo de aprobación genérico para entradas/salidas.'
    list_display = (
        'entrada', 'salida', 'user_aprueba',
        'paso', 'aprobado', 'aprobado_fecha', 'short_comentarios'
    )
    list_filter = ('aprobado', 'aprobado_fecha')
    search_fields = (
        'user_aprueba__username', 'comentarios',
    )
    autocomplete_fields = ('user_aprueba',)
    readonly_fields = ('aprobado_fecha',)
    ordering = ('entrada', 'salida', 'paso')
    list_per_page = 30

    fieldsets = (
        ('Información del flujo', {
            'fields': ('entrada', 'salida', 'user_aprueba', 'paso'),
        }),
        ('Estado y comentarios', {
            'fields': ('aprobado', 'aprobado_fecha', 'comentarios'),
        }),
    )

    actions = ['approve_selected']

    def short_comentarios(self, obj):
        'Texto abreviado de comentarios.'
        return (obj.comentarios[:60] + '...') if obj.comentarios and len(obj.comentarios) > 60 else obj.comentarios
    short_comentarios.short_description = 'Comentarios'

    def approve_selected(self, request, queryset):
        'Acción para aprobar pasos en lote.'
        count = 0
        for paso in queryset.filter(aprobado=False):
            paso.approve()
            count += 1
        self.message_user(request, f'{count} pasos aprobados correctamente.')
    approve_selected.short_description = 'Marcar pasos seleccionados como aprobados'
