from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('sucursal', 'is_manager', 'avatar')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_manager')
