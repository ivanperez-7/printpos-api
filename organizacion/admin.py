from django.contrib import admin

from .models import Sucursal, Almacen, UserProfile


@admin.register(Sucursal)
class SucursalAdmin(admin.ModelAdmin):
    """Admin de sucursales (filiales o unidades del negocio)"""

    list_display = ('nombre', 'direccion', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('nombre', 'direccion')
    ordering = ('nombre',)
    list_editable = ('is_active',)
    list_per_page = 25

    fieldsets = (
        ('Información general', {
            'fields': ('nombre', 'direccion', 'is_active')
        }),
    )


@admin.register(Almacen)
class AlmacenAdmin(admin.ModelAdmin):
    """Admin de almacenes (bodegas) dentro de una sucursal"""

    list_display = ('name', 'branch', 'responsible', 'is_active')
    list_filter = ('branch', 'is_active')
    search_fields = ('name', 'branch__nombre', 'responsible__username')
    autocomplete_fields = ('branch', 'responsible')
    ordering = ('branch', 'name')
    list_editable = ('is_active',)
    list_per_page = 25

    fieldsets = (
        ('Información general', {
            'fields': ('name', 'branch', 'responsible', 'is_active')
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin para los perfiles extendidos de usuario"""

    list_display = ('user', 'role', 'get_branches', 'phone')
    list_filter = ('role', 'branch')
    search_fields = (
        'user__username', 'user__first_name', 'user__last_name', 'phone'
    )
    autocomplete_fields = ('user', 'branch')
    ordering = ('user__username',)
    list_per_page = 25

    fieldsets = (
        ('Usuario vinculado', {
            'fields': ('user', 'role', 'avatar')
        }),
        ('Datos de contacto', {
            'fields': ('phone',)
        }),
        ('Sucursales asignadas', {
            'fields': ('branch',)
        }),
    )

    def get_branches(self, obj):
        """Muestra las sucursales asociadas al usuario."""
        return ", ".join([b.nombre for b in obj.branch.all()])
    
    get_branches.short_description = "Sucursales"
