from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import *


class InventarioModelTest(TestCase):
    def setUp(self):
        self.inventario = Inventario.objects.create(
            nombre="Papel",
            tamano_lote=100,
            precio_lote=500,
            minimo_lotes=2,
            unidades_restantes=250,
            is_active=True
        )

    def test_precio_unidad(self):
        self.assertEqual(self.inventario.precio_unidad, 5.0)

    def test_lotes_restantes(self):
        self.assertEqual(self.inventario.lotes_restantes, 2)

    def test_str(self):
        self.assertIn("Papel", str(self.inventario))


class ProductoModelTest(TestCase):
    def setUp(self):
        self.producto = Producto.objects.create(
            codigo="A001",
            descripcion="Tarjeta",
            abreviado="Tarj",
            categoria="S",
            is_active=True
        )

    def test_str(self):
        self.assertIn("Tarjeta", str(self.producto))


class ProductoGranFormatoModelTest(TestCase):
    def setUp(self):
        self.producto = Producto.objects.create(
            codigo="G001",
            descripcion="Lona",
            abreviado="Lona",
            categoria="G",
            is_active=True
        )
        self.gran_formato = ProductoGranFormato.objects.create(
            producto=self.producto,
            min_m2=2.0,
            precio_m2=150.0
        )

    def test_str(self):
        self.assertIn("Gran Formato", str(self.gran_formato))

    def test_save_invalid_category(self):
        prod_simple = Producto.objects.create(
            codigo="S002",
            descripcion="Simple",
            abreviado="Simp",
            categoria="S",
            is_active=True
        )
        with self.assertRaises(ValueError):
            ProductoGranFormato(producto=prod_simple, min_m2=1, precio_m2=100).save()


class ProductoIntervaloModelTest(TestCase):
    def setUp(self):
        self.producto = Producto.objects.create(
            codigo="A002",
            descripcion="Tarjeta Duplex",
            abreviado="TarjD",
            categoria="S",
            is_active=True
        )
        self.intervalo = ProductoIntervalo.objects.create(
            producto=self.producto,
            desde=10,
            precio_con_iva=120.0,
            duplex=True
        )

    def test_str(self):
        self.assertIn("Dúplex", str(self.intervalo))

    def test_save_invalid_category(self):
        prod_gf = Producto.objects.create(
            codigo="G002",
            descripcion="Lona",
            abreviado="Lona",
            categoria="G",
            is_active=True
        )
        with self.assertRaises(ValueError):
            ProductoIntervalo(producto=prod_gf, desde=1, precio_con_iva=100, duplex=False).save()


class ProductoUtilizaInventarioModelTest(TestCase):
    def setUp(self):
        self.producto = Producto.objects.create(
            codigo="A003",
            descripcion="Tarjeta",
            abreviado="Tarj",
            categoria="S",
            is_active=True
        )
        self.inventario = Inventario.objects.create(
            nombre="Cartulina",
            tamano_lote=50,
            precio_lote=200,
            minimo_lotes=1,
            unidades_restantes=100,
            is_active=True
        )
        self.utiliza = ProductoUtilizaInventario.objects.create(
            producto=self.producto,
            inventario=self.inventario,
            utiliza_inventario=2.0
        )

    def test_str(self):
        self.assertIn("Cartulina", str(self.utiliza))


class ProductoViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.producto_simple = Producto.objects.create(
            codigo="A004",
            descripcion="Tarjeta",
            abreviado="Tarj",
            categoria="S",
            is_active=True
        )
        self.producto_gran_formato = Producto.objects.create(
            codigo="A005",
            descripcion="Metro de lona",
            abreviado="Metro",
            categoria="G",
            is_active=True
        )
        self.intervalo = ProductoIntervalo.objects.create(
            producto=self.producto_simple,
            desde=1,
            precio_con_iva=100.0,
            duplex=False
        )
        self.gran_formato = ProductoGranFormato.objects.create(
            producto=self.producto_gran_formato,
            min_m2=1.0,
            precio_m2=200.0
        )

    def test_list_requires_auth(self):
        url = reverse('producto-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_precio_importe(self):
        self.client.force_authenticate(user=None)
        url = reverse('producto-get-precio-importe', args=[self.producto_simple.id])
        data = {'cantidad': 2, 'descuento_unit': 10.0}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('precio_con_iva', response.data)
        self.assertIn('importe', response.data)

    def test_get_precio_importe_gran_formato(self):
        self.client.force_authenticate(user=None)
        url = reverse('producto-get-precio-importe', args=[self.producto_gran_formato.id])
        data = {'cantidad': 0.7, 'descuento_unit': 5.0}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('precio_con_iva', response.data)
        self.assertIn('importe', response.data)


class InventarioViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.inventario = Inventario.objects.create(
            nombre="Cartulina",
            tamano_lote=50,
            precio_lote=200,
            minimo_lotes=1,
            unidades_restantes=100,
            is_active=True
        )

    def test_list_requires_auth(self):
        url = reverse('inventario-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
