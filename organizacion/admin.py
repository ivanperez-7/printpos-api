from django.contrib import admin

from .models import Cliente, Sucursal, PerfilUsuario, EquipoCliente


class EquipoClienteInline(admin.TabularInline):
    """Inline para mostrar los equipos asignados a un cliente."""
    model = EquipoCliente
    extra = 0


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    inlines = [EquipoClienteInline]
    list_display = (
        'nombre',
        'tipo',
        'rfc',
        'telefono',
        'email',
        'activo',
        'creado',
    )
    list_filter = (
        'tipo',
        'activo',
        'creado',
    )
    search_fields = (
        'nombre',
        'rfc',
        'email',
    )
    ordering = ('nombre',)
    readonly_fields = ('creado', 'actualizado')
    list_per_page = 20


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
        return ', '.join([s.nombre for s in obj.sucursales.all()]) if obj.sucursales.exists() else '-'
    get_sucursales.short_description = 'Sucursales asignadas'
