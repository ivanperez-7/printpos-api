from django.contrib import admin

from .models import EntradaInventario, SalidaInventario


@admin.register(EntradaInventario)
class EntradaInventarioAdmin(admin.ModelAdmin):
    'Gestión de entradas de inventario.'
    list_display = (
        'creado', 'producto', 'cantidad', 'tipo_entrada', 'recibido_por', 'aprobado'
    )
    list_filter = ('tipo_entrada', 'aprobado', 'creado')
    search_fields = (
        'producto__internal_code', 'producto__description', 'numero_factura'
    )
    autocomplete_fields = ('producto', 'recibido_por')
    readonly_fields = ('creado',)
    list_per_page = 25
    date_hierarchy = 'creado'
    ordering = ('-creado',)

    fieldsets = (
        ('Información principal', {
            'fields': (
                'producto', 'tipo_entrada', 'numero_factura',
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
                'nombre_cliente', 'tecnico',
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
