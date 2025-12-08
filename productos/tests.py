from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from .models import Marca, Equipo, Categoría, Proveedor, Producto, Lote, Unidad
from .serializers import (
    CategoriaSerializer, MarcaSerializer, EquipoSerializer, ProveedorSerializer,
    ProductoSerializer, LoteSerializer, UnidadSerializer
)


class MarcaModelTest(APITestCase):
    def test_str(self):
        marca = Marca.objects.create(nombre="Canon")
        self.assertEqual(str(marca), "Canon")


class EquipoModelTest(APITestCase):
    def test_str(self):
        marca = Marca.objects.create(nombre="HP")
        equipo = Equipo.objects.create(nombre="LaserJet", marca=marca)
        self.assertEqual(str(equipo), "LaserJet (HP)")


class CategoriaModelTest(APITestCase):
    def test_str(self):
        categoria = Categoría.objects.create(nombre="Impresoras")
        self.assertEqual(str(categoria), "Impresoras")


class ProveedorModelTest(APITestCase):
    def test_str(self):
        proveedor = Proveedor.objects.create(nombre="Proveedor1")
        self.assertEqual(str(proveedor), "Proveedor1")


class ProductoModelTest(APITestCase):
    def test_str(self):
        categoria = Categoría.objects.create(nombre="Cartuchos")
        proveedor = Proveedor.objects.create(nombre="Proveedor2")
        producto = Producto.objects.create(
            codigo_interno="P001",
            descripcion="Cartucho Negro",
            categoria=categoria,
            unidad_medida="pieza",
            sku="SKU001",
            min_stock=10,
            proveedor=proveedor
        )
        self.assertEqual(str(producto), "P001 (Cartucho Negro)")


class LoteModelTest(APITestCase):
    def test_str(self):
        categoria = Categoría.objects.create(nombre="Cartuchos")
        proveedor = Proveedor.objects.create(nombre="Proveedor3")
        producto = Producto.objects.create(
            codigo_interno="P002",
            descripcion="Cartucho Color",
            categoria=categoria,
            unidad_medida="pieza",
            sku="SKU002",
            min_stock=5,
            proveedor=proveedor
        )
        lote = Lote.objects.create(
            producto=producto,
            codigo_lote="L001",
            cantidad_inicial=100,
            cantidad_restante=100
        )
        self.assertIn("Lote de P002: L001", str(lote))


class UnidadModelTest(APITestCase):
    def test_str(self):
        categoria = Categoría.objects.create(nombre="Cartuchos")
        proveedor = Proveedor.objects.create(nombre="Proveedor4")
        producto = Producto.objects.create(
            codigo_interno="P003",
            descripcion="Cartucho XL",
            categoria=categoria,
            unidad_medida="pieza",
            sku="SKU003",
            min_stock=3,
            proveedor=proveedor
        )
        lote = Lote.objects.create(
            producto=producto,
            codigo_lote="L002",
            cantidad_inicial=50,
            cantidad_restante=50
        )
        unidad = Unidad.objects.create(lote=lote)
        self.assertIn("Unidad de P003, lote L002:", str(unidad))


class CategoriaSerializerTest(APITestCase):
    def test_serializer(self):
        categoria = Categoría.objects.create(nombre="Tinta")
        serializer = CategoriaSerializer(categoria)
        self.assertEqual(serializer.data['nombre'], "Tinta")


class MarcaSerializerTest(APITestCase):
    def test_serializer(self):
        marca = Marca.objects.create(nombre="Epson")
        serializer = MarcaSerializer(marca)
        self.assertEqual(serializer.data['nombre'], "Epson")


class EquipoSerializerTest(APITestCase):
    def test_serializer(self):
        marca = Marca.objects.create(nombre="Brother")
        equipo = Equipo.objects.create(nombre="HL-1234", marca=marca)
        serializer = EquipoSerializer(equipo)
        self.assertEqual(serializer.data['nombre'], "HL-1234")
        self.assertEqual(serializer.data['marca']['nombre'], "Brother")


class ProveedorSerializerTest(APITestCase):
    def test_serializer(self):
        proveedor = Proveedor.objects.create(nombre="Proveedor5")
        serializer = ProveedorSerializer(proveedor)
        self.assertEqual(serializer.data['nombre'], "Proveedor5")


class ProductoSerializerTest(APITestCase):
    def test_serializer(self):
        categoria = Categoría.objects.create(nombre="Papel")
        proveedor = Proveedor.objects.create(nombre="Proveedor6")
        producto = Producto.objects.create(
            codigo_interno="P004",
            descripcion="Papel Bond",
            categoria=categoria,
            unidad_medida="caja",
            sku="SKU004",
            min_stock=20,
            proveedor=proveedor
        )
        serializer = ProductoSerializer(producto)
        self.assertEqual(serializer.data['codigo_interno'], "P004")
        self.assertEqual(serializer.data['categoria']['nombre'], "Papel")
        self.assertEqual(serializer.data['proveedor']['nombre'], "Proveedor6")


class LoteSerializerTest(APITestCase):
    def test_serializer(self):
        categoria = Categoría.objects.create(nombre="Papel")
        proveedor = Proveedor.objects.create(nombre="Proveedor7")
        producto = Producto.objects.create(
            codigo_interno="P005",
            descripcion="Papel Reciclado",
            categoria=categoria,
            unidad_medida="paquete",
            sku="SKU005",
            min_stock=15,
            proveedor=proveedor
        )
        lote = Lote.objects.create(
            producto=producto,
            codigo_lote="L003",
            cantidad_inicial=200,
            cantidad_restante=200
        )
        serializer = LoteSerializer(lote)
        self.assertEqual(serializer.data['codigo_lote'], "L003")


class UnidadSerializerTest(APITestCase):
    def test_serializer(self):
        categoria = Categoría.objects.create(nombre="Papel")
        proveedor = Proveedor.objects.create(nombre="Proveedor8")
        producto = Producto.objects.create(
            codigo_interno="P006",
            descripcion="Papel Fotográfico",
            categoria=categoria,
            unidad_medida="paquete",
            sku="SKU006",
            min_stock=8,
            proveedor=proveedor
        )
        lote = Lote.objects.create(
            producto=producto,
            codigo_lote="L004",
            cantidad_inicial=30,
            cantidad_restante=30
        )
        unidad = Unidad.objects.create(lote=lote)
        serializer = UnidadSerializer(unidad)
        self.assertEqual(serializer.data['lote'], lote.id)


class ProductoViewSetTest(APITestCase):
    def setUp(self):
        self.categoria = Categoría.objects.create(nombre="Accesorios")
        self.proveedor = Proveedor.objects.create(nombre="Proveedor9")
        self.producto = Producto.objects.create(
            codigo_interno="P007",
            descripcion="Cable USB",
            categoria=self.categoria,
            unidad_medida="pieza",
            sku="SKU007",
            min_stock=50,
            proveedor=self.proveedor
        )

    def test_list(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_login(user)

        url = reverse('producto-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['codigo_interno'], "P007")


class LoteViewSetTest(APITestCase):
    def setUp(self):
        self.categoria = Categoría.objects.create(nombre="Accesorios")
        self.proveedor = Proveedor.objects.create(nombre="Proveedor10")
        self.producto = Producto.objects.create(
            codigo_interno="P008",
            descripcion="Cable HDMI",
            categoria=self.categoria,
            unidad_medida="pieza",
            sku="SKU008",
            min_stock=30,
            proveedor=self.proveedor
        )
        self.lote = Lote.objects.create(
            producto=self.producto,
            codigo_lote="L005",
            cantidad_inicial=60,
            cantidad_restante=60
        )

    def test_list(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_login(user)

        url = reverse('lote-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['codigo_lote'], "L005")
