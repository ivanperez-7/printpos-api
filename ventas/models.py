from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from clientes.models import Cliente
from inventario.models import Producto


class Venta(models.Model):
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name="ventas"
    )
    vendedor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="ventas"
    )
    fecha_hora_creacion = models.DateTimeField(default=timezone.now)
    fecha_hora_entrega = models.DateTimeField(default=timezone.now)
    comentarios = models.TextField(blank=True, null=True)
    requiere_factura = models.BooleanField(default=False)
    estado = models.CharField(max_length=50)
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"

    def __str__(self):
        return f"Venta #{self.id} - Cliente: {self.cliente.nombre}"


class VentaDetallado(models.Model):
    venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        related_name="detalles"
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name="detalles_venta"
    )
    cantidad = models.FloatField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.DecimalField(max_digits=10, decimal_places=2)
    especificaciones = models.TextField(blank=True, null=True)
    duplex = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Detalle de Venta"
        verbose_name_plural = "Detalles de Venta"

    def __str__(self):
        return f"Detalle de Venta #{self.venta.id} - {self.producto.descripcion}"
    
    @property
    def importe(self) -> float:
        raise NotImplementedError("Must implement 'importe' property")
