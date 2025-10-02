from django.contrib import admin

from .models import *


class VentaDetalladoInline(admin.TabularInline):
    model = VentaDetallado
    extra = 1


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "cliente",
        "vendedor",
        "fecha_hora_creacion",
        "fecha_hora_entrega",
        "requiere_factura",
        "estado",
    )
    list_filter = ("requiere_factura", "estado", "fecha_hora_creacion")
    search_fields = ("cliente__nombre", "vendedor__first_name", "vendedor__last_name", "estado")
    ordering = ("-fecha_hora_creacion",)
    inlines = [VentaDetalladoInline]
