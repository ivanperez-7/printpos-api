from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from organizacion.models import Cliente
from productos.models import Producto, Lote, Unidad


class Movimiento(models.Model):
    MOV_TYPES = [
        ('entrada', 'Entrada de inventario'),
        ('salida', 'Salida de inventario'),
    ]

    tipo = models.CharField(max_length=10, choices=MOV_TYPES)
    creado = models.DateTimeField(default=timezone.now)
    creado_por = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='movimientos_creados'
    )

    aprobado = models.BooleanField(default=False)
    aprobado_fecha = models.DateTimeField(blank=True, null=True)
    user_aprueba = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='movimientos_aprobados'
    )
    comentarios = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-creado']
        verbose_name = 'Movimiento'
        verbose_name_plural = 'Movimientos'

    def __str__(self):
        return f"Movimiento {self.id} ({self.tipo})"

    def approve(self, user):
        if user.profile.rol != "admin":
            raise PermissionError("Solo administradores pueden aprobar movimientos.")

        self.aprobado = True
        self.aprobado_fecha = timezone.now()
        self.user_aprueba = user
        self.save()

        # delegación: cada tipo sabe cómo procesarse
        if hasattr(self, "detalle_entrada"):
            return self.detalle_entrada.procesar()

        if hasattr(self, "detalle_salida"):
            return self.detalle_salida.procesar()

        raise RuntimeError("Movimiento sin detalle asociado.")


class DetalleEntrada(models.Model):
    movimiento = models.OneToOneField(
        Movimiento, on_delete=models.CASCADE, related_name='detalle_entrada'
    )
    numero_factura = models.CharField(max_length=100)
    recibido_por = models.ForeignKey(User, on_delete=models.PROTECT)

    def procesar(self):
        for item in self.movimiento.items.all():
            item.crear_lote()
        return True
    
    class Meta:
        ordering = ['-movimiento__creado']
        verbose_name = 'Detalles de entrada'
        verbose_name_plural = 'Detalles de entradas'

    def __str__(self):
        return f"Detalle Entrada de Movimiento {self.movimiento.id}"


class DetalleSalida(models.Model):
    movimiento = models.OneToOneField(
        Movimiento, on_delete=models.CASCADE, related_name='detalle_salida'
    )
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='salidas_inventario')
    tecnico = models.CharField(max_length=120, blank=True, null=True)
    requiere_aprobacion = models.BooleanField(default=True)

    class Meta:
        ordering = ['-movimiento__creado']
        verbose_name = 'Detalles de salida'
        verbose_name_plural = 'Detalles de salidas'

    def procesar(self):
        for item in self.movimiento.items.all():
            item.asignar_unidades()
        return True

    def __str__(self):
        return f"Detalle Salida de Movimiento {self.movimiento.id}"


class MovimientoItem(models.Model):
    movimiento = models.ForeignKey(
        Movimiento, on_delete=models.CASCADE, related_name='items'
    )
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.producto.codigo_interno} x {self.cantidad}"

    # Entrada 
    def crear_lote(self):
        codigo = f'{self.producto.codigo_interno}-{timezone.now().strftime("%Y%m%d%H%M%S")}'

        lote = Lote.objects.create(
            producto=self.producto,
            codigo_lote=codigo,
            cantidad_inicial=self.cantidad,
            cantidad_restante=self.cantidad,
        )

        unidades = [Unidad(lote=lote) for _ in range(self.cantidad)]
        Unidad.objects.bulk_create(unidades)
        return lote

    # Salida
    def asignar_unidades(self):
        disponibles = Unidad.objects.filter(
            lote__producto=self.producto,
            status='disponible'
        ).order_by('id')[:self.cantidad]

        if disponibles.count() < self.cantidad:
            raise ValueError(
                f"No hay suficientes unidades de {self.producto.codigo_interno}"
            )

        disponibles.update(status='retirada', actualizado=timezone.now())
        return disponibles
    
    class Meta:
        ordering = ['-movimiento__creado', 'producto__codigo_interno']
        verbose_name = 'Item de movimiento'
        verbose_name_plural = 'Items de movimientos'
