from django.contrib import admin

from .models import InventoryEntry, InventoryExit, ApprovalStep


@admin.register(InventoryEntry)
class InventoryEntryAdmin(admin.ModelAdmin):
    """Configuración del panel para Entradas de Inventario"""

    list_display = (
        'id', 'product', 'supplier', 'entry_type', 'quantity',
        'received_by', 'approved', 'created_at'
    )
    list_filter = ('entry_type', 'approved', 'supplier', 'created_at')
    search_fields = ('product__name', 'product__internal_code', 'invoice_number', 'supplier__name')
    autocomplete_fields = ('product', 'supplier', 'received_by')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Información general', {
            'fields': ('product', 'supplier', 'entry_type', 'invoice_number', 'quantity', 'received_by')
        }),
        ('Detalles adicionales', {
            'fields': ('comments', 'approved'),
            'classes': ('collapse',),
        }),
        ('Auditoría', {
            'fields': ('created_at',),
        }),
    )

    def save_model(self, request, obj, form, change):
        """Aplica automáticamente la entrada al stock si se aprueba."""
        super().save_model(request, obj, form, change)
        if obj.approved:
            obj.apply_to_stock()


@admin.register(InventoryExit)
class InventoryExitAdmin(admin.ModelAdmin):
    """Configuración del panel para Salidas de Inventario"""

    list_display = (
        'id', 'product', 'exit_type', 'quantity', 'technician',
        'delivered_by', 'approved', 'requires_approval', 'created_at'
    )
    list_filter = ('exit_type', 'approved', 'requires_approval', 'created_at')
    search_fields = (
        'product__name', 'product__internal_code', 'client_name', 'technician', 'related_equipment'
    )
    autocomplete_fields = ('product', 'delivered_by')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Información general', {
            'fields': (
                'product', 'exit_type', 'quantity', 'client_name', 'technician',
                'related_equipment', 'delivered_by', 'received_by'
            )
        }),
        ('Autorización', {
            'fields': ('requires_approval', 'approved', 'comments'),
        }),
        ('Auditoría', {
            'fields': ('created_at',),
        }),
    )

    def save_model(self, request, obj, form, change):
        """Descuenta stock automáticamente si la salida es aprobada."""
        super().save_model(request, obj, form, change)
        if obj.approved:
            obj.apply_to_stock()


@admin.register(ApprovalStep)
class ApprovalStepAdmin(admin.ModelAdmin):
    """Configuración del panel para los pasos de aprobación"""

    list_display = (
        'id', 'content_object', 'approver', 'step_order', 'approved', 'approved_at'
    )
    list_filter = ('approved', 'approved_at')
    search_fields = (
        'approver__username', 'approver__first_name', 'approver__last_name',
        'content_type__model'
    )
    autocomplete_fields = ('approver',)
    ordering = ('content_type', 'object_id', 'step_order')

    fieldsets = (
        ('Objeto relacionado', {
            'fields': ('content_type', 'object_id', 'content_object'),
        }),
        ('Flujo de aprobación', {
            'fields': ('approver', 'step_order', 'approved', 'approved_at', 'comments'),
        }),
    )

    readonly_fields = ('approved_at',)

    def approve_selected(self, request, queryset):
        """Acción personalizada para aprobar varios pasos desde el admin."""
        for step in queryset:
            step.approve()
        self.message_user(request, "Pasos de aprobación marcados como aprobados correctamente.")

    actions = ['approve_selected']
    approve_selected.short_description = "Marcar pasos seleccionados como aprobados"
