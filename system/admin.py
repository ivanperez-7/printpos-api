from django.contrib import admin

from .models import SystemConfig


@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ("key", "value", "description", "updated_at")
    search_fields = ("key", "value", "description")
    list_filter = ("updated_at",)
    ordering = ("key",)
    readonly_fields = ("updated_at",)
