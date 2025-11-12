from django.contrib.auth.models import User
from django.db import models


class Sucursal(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Sucursal'
        verbose_name_plural = 'Sucursales'

    def __str__(self):
        return f'{self.nombre} ({self.empresa.nombre})'
    

class Almacen(models.Model):
    '''Almacén físico dentro de una sucursal'''
    name = models.CharField(max_length=100)
    branch = models.ForeignKey(Sucursal, on_delete=models.CASCADE, related_name='almacenes')
    responsible = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Almacén'
        verbose_name_plural = 'Almacenes'
        unique_together = ('name', 'branch')

    def __str__(self):
        return f'{self.name} ({self.branch.name})'


class UserProfile(models.Model):
    '''Extiende la información del usuario (rol, sucursal, etc.)'''
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('operator', 'Operativo'),
        ('viewer', 'Consulta'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='operator')
    phone = models.CharField(max_length=20, blank=True, null=True)
    branch = models.ManyToManyField(Sucursal, blank=True, related_name='usuarios')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'

    def __str__(self):
        return f'{self.user.username} ({self.get_role_display()})'
