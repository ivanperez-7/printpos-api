from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from productos.models import Producto, Lote, Unidad


class EntradaInventario(models.Model):
    ENTRY_TYPES = [
        ('compra', 'Compra / Proveedor'),
        ('devolucion', 'Devolución'),
        ('ajuste', 'Ajuste de inventario'),
    ]

    tipo_entrada = models.CharField(max_length=20, choices=ENTRY_TYPES, default='compra')
    numero_factura = models.CharField(max_length=100, verbose_name='Factura / Orden')
    
    recibido_por = models.ForeignKey(User, on_delete=models.PROTECT, related_name='entradas_recibidas')
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
        return f"Entrada #{self.id} - {self.numero_factura}"

    def approve(self, user: User):
        if user.profile.role != 'admin':
            raise PermissionError("Solo administradores pueden aprobar entradas.")

        self.aprobado = True
        self.aprobado_fecha = timezone.now()
        self.user_aprueba = user
        self.save()

        # Crear lotes + unidades por cada item
        for item in self.items.all():
            item.create_lot()

        return True


class EntradaItem(models.Model):
    entrada = models.ForeignKey(EntradaInventario, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Item de entrada'
        verbose_name_plural = 'Items de entrada'

    def __str__(self):
        return f"{self.producto.codigo_interno} x {self.cantidad}"

    def create_lot(self):
        codigo_lote = f'{self.producto.codigo_interno}-{timezone.now().strftime("%Y%m%d%H%M%S")}'
        
        lote = Lote.objects.create(
            producto=self.producto,
            codigo_lote=codigo_lote,
            cantidad_inicial=self.cantidad,
            cantidad_restante=self.cantidad,
        )
        
        unidades = [Unidad(lote=lote) for _ in range(self.cantidad)]
        Unidad.objects.bulk_create(unidades)

        return lote


class SalidaInventario(models.Model):
    EXIT_TYPES = [
        ('project', 'Proyecto / Cliente'),
        ('rental', 'Equipo en renta'),
        ('internal', 'Uso interno'),
        ('adjustment', 'Ajuste de inventario'),
    ]

    tipo_salida = models.CharField(max_length=20, choices=EXIT_TYPES, default='project')
    nombre_cliente = models.CharField(max_length=150)
    tecnico = models.CharField(max_length=100, blank=True, null=True)

    entregado_por = models.ForeignKey(User, on_delete=models.PROTECT, related_name='salidas_entregadas')
    recibido_por = models.CharField(max_length=100, blank=True, null=True)

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
        return f"Salida #{self.id} - {self.nombre_cliente}"

    def approve(self, user: User):
        if user.profile.role != 'admin':
            raise PermissionError("Solo administradores pueden aprobar salidas.")

        self.aprobado = True
        self.aprobado_fecha = timezone.now()
        self.user_aprueba = user
        self.save()

        # asignar unidades
        for item in self.items.all():
            item.apply_units()

        return True


class SalidaItem(models.Model):
    salida = models.ForeignKey(SalidaInventario, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Item de salida'
        verbose_name_plural = 'Items de salida'

    def __str__(self):
        return f"{self.producto.codigo_interno} x {self.cantidad}"

    def apply_units(self):
        disponibles = Unidad.objects.filter(
            lote__producto=self.producto,
            status='disponible'
        ).order_by('id')[:self.cantidad]

        if disponibles.count() < self.cantidad:
            raise ValueError(f"No hay suficientes unidades de {self.producto.codigo_interno}")

        disponibles.update(status='retirada', actualizado=timezone.now())
        return disponibles
