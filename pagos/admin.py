from django.contrib import admin

from .models import MetodoPago, Caja, VentaPago


@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = ("id", "metodo", "comision_porcentaje")
    search_fields = ("metodo",)
    ordering = ("metodo",)


@admin.register(Caja)
class CajaAdmin(admin.ModelAdmin):
    list_display = ("id", "fecha_hora", "monto", "metodo_pago", "usuario")
    list_filter = ("metodo_pago", "usuario")
    search_fields = ("descripcion", "usuario__usuario")
    ordering = ("-fecha_hora",)


@admin.register(VentaPago)
class VentaPagoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "venta",
        "metodo_pago",
        "fecha_hora",
        "monto",
        "recibido",
        "usuario",
    )
    list_filter = ("metodo_pago", "usuario", "fecha_hora")
    search_fields = ("venta__cliente__nombre", "metodo_pago__metodo")
    ordering = ("-fecha_hora",)
