from django.contrib import admin
from .models import Marca, Categoría, Proveedor, Producto


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    """Administración de marcas."""
    list_display = ('nombre', 'descripcion_resumida')
    search_fields = ('nombre',)
    ordering = ('nombre',)
    list_per_page = 25

    def descripcion_resumida(self, obj):
        return (obj.descripcion[:50] + '...') if obj.descripcion and len(obj.descripcion) > 50 else obj.descripcion
    descripcion_resumida.short_description = "Descripción"


@admin.register(Categoría)
class CategoriaAdmin(admin.ModelAdmin):
    """Administración de categorías de productos."""
    list_display = ('nombre', 'descripcion_resumida')
    search_fields = ('nombre',)
    ordering = ('nombre',)
    list_per_page = 25

    def descripcion_resumida(self, obj):
        return (obj.descripcion[:50] + '...') if obj.descripcion and len(obj.descripcion) > 50 else obj.descripcion
    descripcion_resumida.short_description = "Descripción"


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    """Gestión de proveedores."""
    list_display = ('nombre', 'nombre_contacto', 'telefono', 'correo', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'nombre_contacto', 'telefono', 'correo')
    ordering = ('nombre',)
    list_per_page = 25
    fieldsets = (
        ('Información del proveedor', {
            'fields': ('nombre', 'nombre_contacto', 'telefono', 'correo'),
        }),
        ('Detalles adicionales', {
            'fields': ('direccion', 'activo'),
        }),
    )


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    """Gestión del catálogo de productos."""
    list_display = (
        'codigo_interno', 'descripcion', 'categoria', 'marca', 'proveedor',
        'cantidad_disponible', 'min_stock', 'unidad', 'precio_venta',
    )
    list_filter = ('categoria', 'marca', 'status')
    search_fields = ('codigo_interno', 'descripcion', 'nombre_modelo', 'serie_lote')
    autocomplete_fields = ('categoria', 'marca', 'proveedor')
    list_per_page = 25
    ordering = ('marca__nombre', 'descripcion')

    readonly_fields = ('creado', 'actualizado')
    fieldsets = (
        ('Identificación y descripción', {
            'fields': ('codigo_interno', 'descripcion', 'categoria', 'marca', 'nombre_modelo', 'serie_lote')
        }),
        ('Inventario', {
            'fields': ('cantidad_disponible', 'min_stock', 'unidad')
        }),
        ('Proveedor y precios', {
            'fields': ('proveedor', 'precio_compra', 'precio_venta')
        }),
        ('Estado y control', {
            'fields': ('status', 'notas', 'creado', 'actualizado')
        }),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related('categoria', 'marca', 'proveedor')
        )
