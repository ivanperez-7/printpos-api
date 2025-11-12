from django.contrib.auth.models import User
from django.db import models

from productos.models import Producto


class SystemConfig(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuración del sistema'
        verbose_name_plural = 'Configuraciones del sistema'

    def __str__(self):
        return f'{self.key} = {self.value}'


class ActivityLog(models.Model):
    '''Historial de acciones en el sistema'''
    
    ACTION_CHOICES = [
        ('create', 'Creación'),
        ('update', 'Modificación'),
        ('delete', 'Eliminación'),
        ('approve', 'Aprobación'),
        ('login', 'Inicio de sesión'),
        ('export', 'Exportación de datos'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Registro de actividad'
        verbose_name_plural = 'Registros de actividad'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} - {self.get_action_display()} ({self.created_at.strftime("%Y-%m-%d %H:%M")})'


class InventoryAlert(models.Model):
    '''Alertas automáticas generadas por el sistema'''
    ALERT_TYPES = [
        ('low_stock', 'Bajo stock'),
        ('old_product', 'Producto antiguo'),
        ('unusual_movement', 'Movimiento inusual'),
        ('high_rotation', 'Alta rotación'),
    ]

    product = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='alertas')
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Alerta de inventario'
        verbose_name_plural = 'Alertas de inventario'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_alert_type_display()} - {self.product.internal_code}'
