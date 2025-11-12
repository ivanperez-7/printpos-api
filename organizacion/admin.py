from django.contrib import admin

from .models import Sucursal, Almacen, PerfilUsuario


@admin.register(Sucursal)
class SucursalAdmin(admin.ModelAdmin):
    """Administración de sucursales."""
    list_display = ('nombre', 'direccion', 'activo')
    search_fields = ('nombre', 'direccion')
    list_filter = ('activo',)
    list_per_page = 25
    ordering = ('nombre',)
    fieldsets = (
        ('Información general', {
            'fields': ('nombre', 'direccion', 'activo'),
        }),
    )

    # Mostrar almacenes relacionados directamente desde la sucursal
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('almacenes')


@admin.register(Almacen)
class AlmacenAdmin(admin.ModelAdmin):
    """Administración de almacenes dentro de sucursales."""
    list_display = ('nombre', 'sucursal', 'responsable', 'activo')
    list_filter = ('sucursal', 'activo')
    search_fields = ('nombre', 'sucursal__nombre', 'responsable__username')
    autocomplete_fields = ('sucursal', 'responsable')
    list_per_page = 25
    ordering = ('sucursal__nombre', 'nombre')
    fieldsets = (
        ('Información principal', {
            'fields': ('nombre', 'sucursal', 'responsable', 'activo'),
        }),
    )

    # Mejorar el rendimiento en list_display
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('sucursal', 'responsable')


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    """Gestión de perfiles extendidos de usuario."""
    list_display = ('usuario', 'rol', 'telefono', 'get_sucursales')
    list_filter = ('rol',)
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name', 'telefono')
    autocomplete_fields = ('usuario',)
    filter_horizontal = ('sucursales',)
    list_per_page = 25
    ordering = ('usuario__username',)
    fieldsets = (
        ('Datos personales', {
            'fields': ('usuario', 'rol', 'telefono', 'avatar'),
        }),
        ('Asignación organizacional', {
            'fields': ('sucursales',),
        }),
    )

    def get_sucursales(self, obj):
        """Muestra las sucursales asignadas al usuario."""
        return ", ".join([s.nombre for s in obj.sucursales.all()]) if obj.sucursales.exists() else "-"
    get_sucursales.short_description = "Sucursales asignadas"
