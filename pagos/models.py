from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from ventas.models import Venta


class MetodoPago(models.Model):
    metodo = models.CharField(max_length=30, unique=True)
    comision_porcentaje = models.FloatField(default=0.0)

    class Meta:
        verbose_name = "Método de Pago"
        verbose_name_plural = "Métodos de Pago"

    def __str__(self):
        return f"{self.metodo} ({self.comision_porcentaje}%)"


class Caja(models.Model):
    fecha_hora = models.DateTimeField(default=timezone.now)
    monto = models.FloatField()
    descripcion = models.TextField(blank=True, null=True)
    metodo_pago = models.ForeignKey(
        MetodoPago,
        on_delete=models.PROTECT,
        related_name="movimientos_caja"
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="movimientos_caja"
    )

    class Meta:
        verbose_name = "Movimiento de Caja"
        verbose_name_plural = "Movimientos de Caja"
        ordering = ("-fecha_hora",)

    def __str__(self):
        return f"Movimiento {self.id} - {self.monto} ({self.metodo_pago.metodo})"


class VentaPago(models.Model):
    venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        related_name="pagos"
    )
    metodo_pago = models.ForeignKey(
        MetodoPago,
        on_delete=models.PROTECT,
        related_name="pagos"
    )
    fecha_hora = models.DateTimeField(default=timezone.now)
    monto = models.FloatField()
    recibido = models.FloatField(blank=True, null=True)
    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="pagos_registrados"
    )

    class Meta:
        verbose_name = "Pago de Venta"
        verbose_name_plural = "Pagos de Ventas"
        ordering = ("-fecha_hora",)

    def __str__(self):
        return f"Pago #{self.id} - Venta {self.venta.id} ({self.metodo_pago.metodo})"
