from django.contrib import admin

from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "telefono", "correo", "cliente_especial")
    list_filter = ("cliente_especial",)
    search_fields = ("nombre", "telefono", "correo", "rfc")
    ordering = ("nombre",)
    fieldsets = (
        (None, {
            "fields": ("nombre", "telefono", "correo", "direccion", "rfc")
        }),
        ("Opciones adicionales", {
            "fields": ("cliente_especial", "descuentos"),
            "classes": ("collapse",),
        }),
    )
