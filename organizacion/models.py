from django.contrib.auth.models import AbstractUser
from django.db import models


class Empresa(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.nombre


class Sucursal(models.Model):
    empresa = models.ForeignKey(Empresa, related_name='sucursales', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        unique_together = ('empresa', 'nombre')

    def __str__(self):
        return f"{self.nombre} ({self.empresa.nombre})"


class Usuario(AbstractUser):
    sucursal = models.ManyToManyField(Sucursal, blank=True, related_name='usuarios')
    is_manager = models.BooleanField(default=False)
