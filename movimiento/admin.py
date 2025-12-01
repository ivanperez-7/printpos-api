from django.contrib import admin

from .models import EntradaInventario, EntradaItem, SalidaInventario, SalidaItem


class EntradaItemInline(admin.TabularInline):
    model = EntradaItem
    extra = 1


class SalidaItemInline(admin.TabularInline):
    model = SalidaItem
    extra = 1


@admin.register(EntradaInventario)
class EntradaInventarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'numero_factura', 'tipo_entrada', 'aprobado', 'creado')
    list_filter = ('tipo_entrada', 'aprobado', 'creado')
    search_fields = ('numero_factura', 'comentarios')

    inlines = [EntradaItemInline]

    readonly_fields = ('aprobado', 'aprobado_fecha', 'user_aprueba', 'creado')


@admin.register(SalidaInventario)
class SalidaInventarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_cliente', 'tipo_salida', 'aprobado', 'creado')
    list_filter = ('tipo_salida', 'aprobado', 'creado')
    search_fields = ('nombre_cliente', 'comentarios')

    inlines = [SalidaItemInline]

    readonly_fields = ('aprobado', 'aprobado_fecha', 'user_aprueba', 'creado')
