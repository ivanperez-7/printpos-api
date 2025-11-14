from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from productos.models import Producto, Proveedor


class EntradaInventario(models.Model):
    ENTRY_TYPES = [
        ('compra', 'Compra / Proveedor'),
        ('devolucion', 'Devolución'),
        ('ajuste', 'Ajuste de inventario'),
    ]

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='entradas')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)
    tipo_entrada = models.CharField(max_length=20, choices=ENTRY_TYPES, default='compra')

    numero_factura = models.CharField(max_length=100, blank=True, null=True, verbose_name='Factura / Orden de compra')
    cantidad = models.PositiveIntegerField(verbose_name='Cantidad ingresada')
    recibido_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='entradas_recibidas')

    user_aprueba = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='aprobaciones_entradas')
    aprobado = models.BooleanField(default=False)
    aprobado_fecha = models.DateTimeField(blank=True, null=True)

    comentarios = models.TextField(blank=True, null=True)
    creado = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Entrada de inventario'
        verbose_name_plural = 'Entradas de inventario'
        ordering = ['-creado']

    def __str__(self):
        return f'Entrada {self.producto.codigo_interno} ({self.cantidad}) - {self.creado.strftime("%Y-%m-%d")}'

    def aplicar_a_stock(self):
        """Aumenta el stock del producto según la cantidad."""
        self.producto.cantidad_disponible += self.cantidad
        self.producto.save()
    
    def approve(self, user: User):
        """Marca el paso como aprobado."""
        self.aprobado = True
        self.aprobado_fecha = timezone.now()
        self.user_aprueba = user
        self.save()


class SalidaInventario(models.Model):
    EXIT_TYPES = [
        ('project', 'Proyecto / Cliente'),
        ('rental', 'Equipo en renta'),
        ('internal', 'Uso interno'),
        ('adjustment', 'Ajuste de inventario'),
    ]

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='salidas')
    tipo_salida = models.CharField(max_length=20, choices=EXIT_TYPES, default='project')

    nombre_cliente = models.CharField(max_length=150, blank=True, null=True)
    tecnico = models.CharField(max_length=100, blank=True, null=True, verbose_name='Técnico responsable')
    equipo_asociado = models.CharField(max_length=150, blank=True, null=True, verbose_name='Equipo asociado')

    cantidad = models.PositiveIntegerField(verbose_name='Cantidad entregada')
    entregado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='salidas_entregadas')
    recibido_por = models.CharField(max_length=100, blank=True, null=True, verbose_name='Recibido por')

    requiere_aprobacion = models.BooleanField(default=False)
    user_aprueba = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='aprobaciones_salidas')
    aprobado = models.BooleanField(default=False)
    aprobado_fecha = models.DateTimeField(blank=True, null=True)

    comentarios = models.TextField(blank=True, null=True)
    creado = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Salida de inventario'
        verbose_name_plural = 'Salidas de inventario'
        ordering = ['-creado']

    def __str__(self):
        return f'Salida {self.producto.codigo_interno} ({self.cantidad}) - {self.creado.strftime("%Y-%m-%d")}'

    def aplicar_a_stock(self):
        """Reduce el stock del producto según la cantidad."""
        if self.producto.cantidad_disponible >= self.cantidad:
            self.producto.cantidad_disponible -= self.cantidad
            self.producto.save()
        else:
            raise ValueError('Stock insuficiente para realizar la salida.')
    
    def approve(self, user: User):
        """Marca el paso como aprobado."""
        self.aprobado = True
        self.aprobado_fecha = timezone.now()
        self.user_aprueba = user
        self.save()
