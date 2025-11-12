from django.contrib import admin

from .models import Marca, Categoría, Proveedor, Producto


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    """Administración del catálogo de marcas"""
    list_display = ('name', 'description')
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 25

    fieldsets = (
        ('Información de la marca', {
            'fields': ('name', 'description'),
        }),
    )


@admin.register(Categoría)
class CategoriaAdmin(admin.ModelAdmin):
    """Administración de categorías de productos"""
    list_display = ('name', 'description')
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 25

    fieldsets = (
        ('Información de la categoría', {
            'fields': ('name', 'description'),
        }),
    )


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    """Administración del catálogo de proveedores"""
    list_display = ('name', 'contact_name', 'phone', 'email', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'contact_name', 'email', 'phone')
    list_editable = ('is_active',)
    ordering = ('name',)
    list_per_page = 25

    fieldsets = (
        ('Datos principales', {
            'fields': ('name', 'is_active'),
        }),
        ('Contacto', {
            'fields': ('contact_name', 'phone', 'email'),
        }),
        ('Dirección', {
            'fields': ('address',),
        }),
    )


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    """Administración del catálogo principal de productos"""

    list_display = (
        'internal_code', 'description', 'brand', 'category',
        'quantity_available', 'min_stock', 'is_low_stock', 'status'
    )
    list_filter = ('brand', 'category', 'status')
    search_fields = (
        'internal_code', 'description', 'model_name',
        'serial_or_lot', 'brand__name', 'category__name'
    )
    autocomplete_fields = ('brand', 'category', 'supplier')
    ordering = ('brand__name', 'description')
    list_editable = ('min_stock', 'status')
    readonly_fields = ('created_at', 'updated_at', 'age_in_days')
    list_per_page = 25

    fieldsets = (
        ('Información general', {
            'fields': (
                'internal_code', 'description', 'category', 'brand',
                'model_name', 'serial_or_lot', 'unit', 'status'
            )
        }),
        ('Inventario', {
            'fields': ('quantity_available', 'min_stock'),
        }),
        ('Proveedor y precios', {
            'fields': ('supplier', 'purchase_price', 'sale_price'),
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at', 'age_in_days'),
            'classes': ('collapse',),
        }),
        ('Notas adicionales', {
            'fields': ('notes',),
            'classes': ('collapse',),
        }),
    )

    def is_low_stock(self, obj):
        """Muestra un ícono visual o texto si está por debajo del mínimo."""
        return "⚠️ Sí" if obj.is_low_stock else "✅ No"
    
    is_low_stock.short_description = "Stock bajo"
