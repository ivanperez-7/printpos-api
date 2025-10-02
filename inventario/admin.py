from django.contrib import admin

from .models import *


@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nombre",
        "tamano_lote",
        "precio_lote",
        "precio_unidad",
        "minimo_lotes",
        "unidades_restantes",
        "lotes_restantes",
    )
    search_fields = ("nombre",)
    ordering = ("nombre",)
    list_filter = ("minimo_lotes",)
    readonly_fields = ("precio_unidad", "lotes_restantes")


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("id", "codigo", "descripcion", "abreviado", "categoria", "is_active")
    search_fields = ("codigo", "descripcion", "abreviado", "categoria")
    list_filter = ("is_active", "categoria")
    ordering = ("descripcion",)


@admin.register(ProductoGranFormato)
class ProductoGranFormatoAdmin(admin.ModelAdmin):
    list_display = ("producto", "min_m2", "precio_m2")
    search_fields = ("producto__descripcion",)
    ordering = ("producto",)


@admin.register(ProductoIntervalo)
class ProductoIntervaloAdmin(admin.ModelAdmin):
    list_display = ("producto", "desde", "precio_con_iva", "duplex")
    list_filter = ("duplex",)
    search_fields = ("producto__descripcion",)
    ordering = ("producto", "desde")


@admin.register(ProductoUtilizaInventario)
class ProductoUtilizaInventarioAdmin(admin.ModelAdmin):
    list_display = ("producto", "inventario", "utiliza_inventario")
    list_filter = ("inventario",)
    search_fields = ("producto__descripcion", "inventario__nombre")
    ordering = ("producto", "inventario")
