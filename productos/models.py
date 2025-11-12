from django.db import models
from django.utils import timezone


class Marca(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Categoría(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Proveedor(models.Model):
    nombre = models.CharField(max_length=150)
    nombre_contacto = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    correo = models.EmailField(blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    STATUS_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('descontinuado', 'Descontinuado'),
    ]

    codigo_interno = models.CharField(max_length=50, unique=True, verbose_name='Código interno')
    descripcion = models.CharField(max_length=255, verbose_name='Descripción')
    categoria = models.ForeignKey(Categoría, on_delete=models.SET_NULL, null=True, related_name='productos')
    marca = models.ForeignKey(Marca, on_delete=models.SET_NULL, null=True, related_name='productos')
    nombre_modelo = models.CharField(max_length=100, blank=True, null=True, verbose_name='Modelo')
    serie_lote = models.CharField(max_length=100, blank=True, null=True, verbose_name='Número de serie/lote')

    cantidad_disponible = models.PositiveIntegerField(default=0, verbose_name='Cantidad disponible')
    min_stock = models.PositiveIntegerField(default=0, verbose_name='Stock mínimo')
    unidad = models.CharField(max_length=50, default='pieza', verbose_name='Unidad de medida')

    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos')
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    creado = models.DateTimeField(default=timezone.now)
    actualizado = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    notas = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['marca__nombre', 'descripcion']

    def __str__(self):
        return f'{self.codigo_interno} - {self.descripcion}'

    @property
    def stock_bajo(self):
        '''Devuelve True si el producto está por debajo del stock mínimo.'''
        return self.cantidad_disponible <= self.min_stock

    @property
    def edad_en_dias(self):
        '''Días desde la creación del registro (para alertas de antigüedad).'''
        return (timezone.now().date() - self.creado.date()).days
