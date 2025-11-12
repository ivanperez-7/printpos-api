from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.utils import timezone

from productos.models import Producto, Proveedor


class InventoryEntry(models.Model):
    '''Registro de entradas de inventario (compras, devoluciones, ajustes)'''

    ENTRY_TYPES = [
        ('purchase', 'Compra / Proveedor'),
        ('return', 'Devolución'),
        ('adjustment', 'Ajuste de inventario'),
    ]

    product = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='entradas')
    supplier = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPES, default='purchase')

    invoice_number = models.CharField(max_length=100, blank=True, null=True, verbose_name='Factura / Orden de compra')
    quantity = models.PositiveIntegerField(verbose_name='Cantidad ingresada')
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='entradas_recibidas')

    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    approved = models.BooleanField(default=True)  # True por defecto para entradas simples

    class Meta:
        verbose_name = 'Entrada de inventario'
        verbose_name_plural = 'Entradas de inventario'
        ordering = ['-created_at']

    def __str__(self):
        return f'Entrada {self.product.internal_code} ({self.quantity}) - {self.created_at.strftime("%Y-%m-%d")}'

    def apply_to_stock(self):
        '''Aumenta el stock del producto según la cantidad.'''
        self.product.quantity_available += self.quantity
        self.product.save()


class InventoryExit(models.Model):
    '''Registro de salidas de inventario (clientes, técnicos, proyectos, etc.)'''

    EXIT_TYPES = [
        ('project', 'Proyecto / Cliente'),
        ('rental', 'Equipo en renta'),
        ('internal', 'Uso interno'),
        ('adjustment', 'Ajuste de inventario'),
    ]

    product = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='salidas')
    exit_type = models.CharField(max_length=20, choices=EXIT_TYPES, default='project')

    client_name = models.CharField(max_length=150, blank=True, null=True)
    technician = models.CharField(max_length=100, blank=True, null=True, verbose_name='Técnico responsable')
    related_equipment = models.CharField(max_length=150, blank=True, null=True, verbose_name='Equipo asociado')

    quantity = models.PositiveIntegerField(verbose_name='Cantidad entregada')
    delivered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='salidas_entregadas')
    received_by = models.CharField(max_length=100, blank=True, null=True, verbose_name='Recibido por')

    requires_approval = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    comments = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Salida de inventario'
        verbose_name_plural = 'Salidas de inventario'
        ordering = ['-created_at']

    def __str__(self):
        return f'Salida {self.product.internal_code} ({self.quantity}) - {self.created_at.strftime("%Y-%m-%d")}'

    def apply_to_stock(self):
        '''Reduce el stock del producto según la cantidad.'''
        if self.product.quantity_available >= self.quantity:
            self.product.quantity_available -= self.quantity
            self.product.save()
        else:
            raise ValueError('Stock insuficiente para realizar la salida.')


class ApprovalStep(models.Model):
    '''Flujo de aprobación configurable para cualquier tipo de objeto (entrada, salida, etc.)'''

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.BigIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='pasos_aprobacion')
    step_order = models.PositiveIntegerField(default=1)
    approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Paso de aprobación'
        verbose_name_plural = 'Flujo de aprobaciones'
        ordering = ['content_type', 'object_id', 'step_order']

    def __str__(self):
        return f'Aprobación {self.step_order} para {self.content_object}'

    def approve(self):
        '''Marca el paso como aprobado.'''
        self.approved = True
        self.approved_at = timezone.now()
        self.save()
