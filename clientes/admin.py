from django.contrib import admin

from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "telefono", "correo", "cliente_especial", "is_active")
    list_filter = ("cliente_especial", "is_active")
    search_fields = ("nombre", "telefono", "correo", "rfc")
    ordering = ("nombre",)
    fieldsets = (
        (None, {
            "fields": ("nombre", "telefono", "correo", "direccion", "rfc", "is_active")
        }),
        ("Opciones adicionales", {
            "fields": ("cliente_especial", "descuentos"),
            "classes": ("collapse",),
        }),
    )
