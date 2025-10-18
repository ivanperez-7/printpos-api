from math import ceil

from django.db import models
from django.db.transaction import atomic
from django.utils import timezone

from clientes.models import Cliente
from inventario.models import Producto
from organizacion.models import Usuario


class Venta(models.Model):
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name="ventas"
    )
    vendedor = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="ventas"
    )
    fecha_hora_creacion = models.DateTimeField(default=timezone.now)
    fecha_hora_entrega = models.DateTimeField(default=timezone.now)
    comentarios = models.TextField(blank=True, null=True)
    requiere_factura = models.BooleanField(default=False)
    estado = models.CharField(max_length=50, default='No terminada')
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
    
    def save(self, *args, **kwargs):
        if self.is_active and self.__class__.objects.filter(vendedor=self.vendedor, is_active=True).exclude(id=self.id).exists():
            raise ValueError("Ya existe una venta activa para este usuario.")
        return super().save(*args, **kwargs)
    
    @atomic
    def cancelar(self, regresar_inventario: bool = True, registrar_devoluciones: bool = True):
        if self.estado == 'Cancelada':
            raise ValueError("La venta ya está cancelada.")
        
        self.estado = 'Cancelada'
        self.is_active = False
        self.save()

        if regresar_inventario:
            for detalle in self.detalles.all():
                for pu in detalle.producto.inventarios.all():
                    ajuste = (detalle.cantidad * pu.utiliza_inventario) / (2 if detalle.duplex else 1)
                    pu.inventario.unidades_restantes += ceil(ajuste)
                    pu.inventario.save()
        if registrar_devoluciones:
            for pago in self.pagos.all():
                self.pagos.create(
                    metodo_pago=pago.metodo_pago,
                    monto=-pago.monto,
                    usuario=pago.usuario
                )

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
    
    @atomic
    def save(self, *args, **kwargs):
        if self._state.adding:  # Solo ajustar inventario al ser nuevo
            for pu in self.producto.inventarios.all():
                ajuste = (self.cantidad * pu.utiliza_inventario) / (2 if self.duplex else 1)
                pu.inventario.unidades_restantes -= ceil(ajuste)
                pu.inventario.save()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Detalle de Venta #{self.venta.id} - {self.producto.descripcion}"
    
    @property
    def importe(self) -> float:
        raise NotImplementedError("Must implement 'importe' property")
