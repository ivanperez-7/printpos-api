from django.contrib import admin

from .models import ConfiguracionSistema, RegistroActividad, AlertaInventario


@admin.register(ConfiguracionSistema)
class ConfiguracionSistemaAdmin(admin.ModelAdmin):
    """Admin para las configuraciones globales del sistema."""
    list_display = ('clave', 'valor_resumido', 'actualizado')
    search_fields = ('clave', 'valor', 'descripcion')
    list_per_page = 25
    ordering = ('clave',)

    def valor_resumido(self, obj):
        return (obj.valor[:50] + '...') if obj.valor and len(obj.valor) > 50 else obj.valor
    valor_resumido.short_description = 'Valor'


@admin.register(RegistroActividad)
class RegistroActividadAdmin(admin.ModelAdmin):
    """Admin para el historial de acciones del sistema."""
    list_display = ('usuario', 'descripcion_resumida', 'creado')
    list_filter = ('accion', 'usuario')
    search_fields = ('usuario__username', 'descripcion')
    readonly_fields = ('usuario', 'accion', 'descripcion', 'creado')
    list_per_page = 30
    date_hierarchy = 'creado'
    ordering = ('-creado',)

    def descripcion_resumida(self, obj):
        return (obj.descripcion[:60] + '...') if len(obj.descripcion) > 60 else obj.descripcion
    descripcion_resumida.short_description = 'Descripción'


@admin.register(AlertaInventario)
class AlertaInventarioAdmin(admin.ModelAdmin):
    """Admin para la gestión de alertas automáticas del inventario."""
    list_display = ('producto', 'mensaje_resumido', 'resuelto', 'creado')
    list_filter = ('tipo_alerta', 'resuelto')
    search_fields = ('producto__codigo_interno', 'mensaje')
    list_per_page = 25
    readonly_fields = ('producto', 'tipo_alerta', 'mensaje', 'creado')
    ordering = ('-creado',)

    def mensaje_resumido(self, obj):
        return (obj.mensaje[:60] + '...') if len(obj.mensaje) > 60 else obj.mensaje
    mensaje_resumido.short_description = 'Mensaje'

