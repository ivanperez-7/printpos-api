from django.contrib import admin

from .models import SystemConfig, ActivityLog, InventoryAlert


@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    """Configuración general del sistema (parámetros clave-valor)."""
    list_display = ('key', 'short_value', 'updated_at')
    search_fields = ('key', 'value')
    ordering = ('key',)
    list_per_page = 25
    readonly_fields = ('updated_at',)

    fieldsets = (
        ('Configuración', {
            'fields': ('key', 'value', 'description'),
        }),
        ('Auditoría', {
            'fields': ('updated_at',),
        }),
    )

    def short_value(self, obj):
        """Muestra el valor recortado para evitar que la lista sea muy larga."""
        return (obj.value[:50] + '...') if obj.value and len(obj.value) > 50 else obj.value
    short_value.short_description = "Valor"


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    """Historial de acciones de usuarios en el sistema."""
    list_display = ('created_at', 'user', 'action', 'short_description')
    list_filter = ('action', 'created_at')
    search_fields = ('user__username', 'description')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    readonly_fields = ('user', 'action', 'description', 'created_at')
    list_per_page = 30

    fieldsets = (
        ('Detalle de actividad', {
            'fields': ('user', 'action', 'description', 'created_at'),
        }),
    )

    def short_description(self, obj):
        """Texto acortado para vista en lista."""
        return (obj.description[:60] + '...') if len(obj.description) > 60 else obj.description
    short_description.short_description = "Descripción"


@admin.register(InventoryAlert)
class InventoryAlertAdmin(admin.ModelAdmin):
    """Alertas automáticas generadas por el sistema (stock, movimientos, etc.)."""
    list_display = (
        'created_at', 'alert_type', 'product', 'short_message', 'resolved'
    )
    list_filter = ('alert_type', 'resolved', 'created_at')
    search_fields = ('product__internal_code', 'message', 'product__description')
    autocomplete_fields = ('product',)
    list_editable = ('resolved',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_per_page = 30

    fieldsets = (
        ('Información de la alerta', {
            'fields': ('product', 'alert_type', 'message', 'resolved'),
        }),
        ('Auditoría', {
            'fields': ('created_at',),
        }),
    )

    def short_message(self, obj):
        """Texto abreviado del mensaje."""
        return (obj.message[:60] + '...') if len(obj.message) > 60 else obj.message
    
    short_message.short_description = "Mensaje"
