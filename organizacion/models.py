from django.contrib.auth.models import User
from django.db import models


class Cliente(models.Model):
    TIPO_PERSONA = [
        ('fisica', 'Persona Física'),
        ('moral', 'Persona Moral'),
    ]

    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=10, choices=TIPO_PERSONA, default='fisica')

    rfc = models.CharField(max_length=13, blank=True, null=True, unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    direccion = models.TextField(blank=True, null=True)

    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Sucursal(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Sucursal'
        verbose_name_plural = 'Sucursales'

    def __str__(self):
        return f'{self.nombre} ({self.empresa.nombre})'


class PerfilUsuario(models.Model):
    """Extiende la información del usuario (rol, sucursal, etc.)"""
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('operativo', 'Operativo'),
        ('consulta', 'Consulta'),
    ]

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    rol = models.CharField(max_length=20, choices=ROLE_CHOICES, default='operativo')
    telefono = models.CharField(max_length=20, blank=True, null=True)
    sucursales = models.ManyToManyField(Sucursal, blank=True, related_name='usuarios')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'

    def __str__(self):
        return f'{self.usuario.username} ({self.get_rol_display()})'
