from decimal import Decimal

from django.db import models


class Inventario(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    tamano_lote = models.FloatField()
    precio_lote = models.DecimalField(max_digits=10, decimal_places=2)
    minimo_lotes = models.FloatField()
    unidades_restantes = models.FloatField()
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Inventario"
        verbose_name_plural = "Inventarios"

    def __str__(self):
        return f"{self.nombre} - Lotes restantes: {self.lotes_restantes}"

    @property
    def precio_unidad(self) -> float:
        if self.tamano_lote:
            return self.precio_lote / Decimal(str(self.tamano_lote))
        return 0.0

    @property
    def lotes_restantes(self) -> int:
        if self.tamano_lote:
            return int(self.unidades_restantes // self.tamano_lote)
        return 0


class Producto(models.Model):
    categorias_choices = [
        ("S", "Simple"),
        ("G", "Gran Formato")
    ]

    codigo = models.CharField(max_length=100, unique=True)
    descripcion = models.CharField(max_length=100)
    abreviado = models.CharField(max_length=50)
    categoria = models.CharField(max_length=50, choices=categorias_choices)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def obtener_precio_importe_simple(self, cantidad: int, desc_unit: float = 0., duplex: bool = False):
        """ Obtiene el precio e importe para un producto de categoría simple."""
        if self.categoria != 'S':
            raise ValueError('El producto no es de categoría simple.')

        intervalos = self.intervalos.filter(desde__lte=cantidad).order_by('-desde', '-duplex')
        if not duplex:
            intervalos = intervalos.exclude(duplex=True)
        if intervalo := intervalos.first():
            importe = (intervalo.precio_con_iva - Decimal(str(desc_unit))) * Decimal(str(cantidad))
            return intervalo.precio_con_iva, importe
        raise ValueError('No hay un intervalo que cubra la cantidad solicitada.')

    def obtener_precio_importe_gran_formato(self, m2: float, desc_unit: float = 0.):
        """ Obtiene el precio e importe para un producto de categoría gran formato."""
        if self.categoria != 'G':
            raise ValueError('El producto no es de categoría gran formato.')
        if not self.gran_formato:
            raise ValueError('El producto no tiene definido un precio de gran formato.')

        m2 = max(m2, self.gran_formato.min_m2)
        importe = (self.gran_formato.precio_m2 - Decimal(str(desc_unit))) * Decimal(str(m2))
        return self.gran_formato.precio_m2, importe

    def __str__(self):
        return f"{self.descripcion} ({self.codigo})"


class ProductoGranFormato(models.Model):
    producto = models.OneToOneField(
        Producto,
        on_delete=models.CASCADE,
        related_name="gran_formato",
        limit_choices_to={'categoria': 'G'}
    )
    min_m2 = models.FloatField()
    precio_m2 = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Producto Gran Formato"
        verbose_name_plural = "Productos Gran Formato"

    def save(self, *args, **kwargs):
        if self.producto.categoria == 'S':
            raise ValueError('El producto es de categoría simple y se quieren insertar metros.')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.producto.descripcion} - Gran Formato"


class ProductoIntervalo(models.Model):
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name="intervalos",
        limit_choices_to={'categoria': 'S'}
    )
    desde = models.PositiveIntegerField()
    precio_con_iva = models.DecimalField(max_digits=10, decimal_places=2)
    duplex = models.BooleanField()

    class Meta:
        verbose_name = "Producto Intervalo"
        verbose_name_plural = "Productos Intervalos"
        unique_together = ("producto", "desde", "duplex")

    def save(self, *args, **kwargs):
        if self.producto.categoria == 'G':
            raise ValueError('El producto es de categoría gran formato y se quieren insertar intervalos.')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.producto.descripcion} - Desde {self.desde} ({'Dúplex' if self.duplex else 'Simple'})"


class ProductoUtilizaInventario(models.Model):
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name="inventarios"
    )
    inventario = models.ForeignKey(
        Inventario,
        on_delete=models.CASCADE,
        related_name="productos"
    )
    utiliza_inventario = models.FloatField()

    class Meta:
        verbose_name = "Producto utiliza Inventario"
        verbose_name_plural = "Productos utilizan Inventario"
        unique_together = ("producto", "inventario")

    def __str__(self):
        return f"{self.producto.descripcion} usa {self.utiliza_inventario} de {self.inventario.nombre}"
