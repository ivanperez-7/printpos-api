from django.db import models
from django.utils import timezone


class Marca(models.Model):
    '''Catálogo de marcas (Konica, Fuji, Katun, etc.)'''
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
        ordering = ['name']

    def __str__(self):
        return self.name


class Categoría(models.Model):
    '''Categoría general de productos (Impresoras, Refacciones, Consumibles, etc.)'''
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['name']

    def __str__(self):
        return self.name


class Proveedor(models.Model):
    '''Catálogo de proveedores'''
    name = models.CharField(max_length=150)
    contact_name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['name']

    def __str__(self):
        return self.name


class Producto(models.Model):
    '''Catálogo principal de productos en el inventario'''

    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('inactive', 'Inactivo'),
        ('discontinued', 'Descontinuado'),
    ]

    internal_code = models.CharField(max_length=50, unique=True, verbose_name='Código interno')
    description = models.CharField(max_length=255, verbose_name='Descripción')
    category = models.ForeignKey(Categoría, on_delete=models.SET_NULL, null=True, related_name='productos')
    brand = models.ForeignKey(Marca, on_delete=models.SET_NULL, null=True, related_name='productos')
    model_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='Modelo')
    serial_or_lot = models.CharField(max_length=100, blank=True, null=True, verbose_name='Número de serie/lote')

    quantity_available = models.PositiveIntegerField(default=0, verbose_name='Cantidad disponible')
    min_stock = models.PositiveIntegerField(default=0, verbose_name='Stock mínimo')
    unit = models.CharField(max_length=50, default='pieza', verbose_name='Unidad de medida')

    supplier = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos')
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['brand__name', 'description']

    def __str__(self):
        return f'{self.internal_code} - {self.description}'

    @property
    def is_low_stock(self):
        '''Devuelve True si el producto está por debajo del stock mínimo.'''
        return self.quantity_available <= self.min_stock

    @property
    def age_in_days(self):
        '''Días desde la creación del registro (para alertas de antigüedad).'''
        return (timezone.now().date() - self.created_at.date()).days
