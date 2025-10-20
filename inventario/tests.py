from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import *
from .serializers import *
from organizacion.models import Usuario


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
        self.inventario.refresh_from_db()

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
            precio_m2=150.0000000012487924
        )

    def test_str(self):
        self.assertIn("Gran Formato", str(self.gran_formato))
    
    def test_decimal_fields(self):
        self.assertIsInstance(self.gran_formato.precio_m2, float)
        self.gran_formato.refresh_from_db()
        self.assertIsInstance(self.gran_formato.precio_m2, Decimal)
        self.assertEqual(self.gran_formato.precio_m2, Decimal('150.00'))

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
            precio_con_iva=119.9999991238742,
            duplex=True
        )
    
    def test_decimal_fields(self):
        self.assertIsInstance(self.intervalo.precio_con_iva, float)
        self.intervalo.refresh_from_db()
        self.assertIsInstance(self.intervalo.precio_con_iva, Decimal)
        self.assertEqual(self.intervalo.precio_con_iva, Decimal('120.00'))

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


class ProductoSerializerTest(TestCase):
    def setUp(self):
        self.producto = Producto.objects.create(
            codigo="T001",
            descripcion="Tarjeta Test",
            abreviado="TarjTest",
            categoria="S",
            is_active=True
        )
        self.producto_gran_formato = Producto.objects.create(
            codigo="T002",
            descripcion="Lona Test",
            abreviado="Lona",
            categoria="G",
            is_active=True
        )
        self.inventario = Inventario.objects.create(
            nombre="Cartulina Test",
            tamano_lote=100,
            precio_lote=500,
            minimo_lotes=2,
            unidades_restantes=250,
            is_active=True
        )
        self.intervalo = ProductoIntervalo.objects.create(
            producto=self.producto,
            desde=10,
            precio_con_iva=120.0,
            duplex=True
        )
        self.gran_formato = ProductoGranFormato.objects.create(
            producto=self.producto_gran_formato,
            min_m2=2.0,
            precio_m2=150.0
        )
        self.utiliza = ProductoUtilizaInventario.objects.create(
            producto=self.producto,
            inventario=self.inventario,
            utiliza_inventario=2.0
        )

    def test_serialize_producto_with_nested(self):
        serializer = ProductoSerializer(instance=self.producto)
        data = serializer.data
        self.assertEqual(data['codigo'], "T001")
        self.assertIn('intervalos', data)
        self.assertIn('gran_formato', data)
        self.assertIn('inventarios', data)
        self.assertIsInstance(data['intervalos'], list)
        self.assertIsInstance(data['inventarios'], list)
        self.assertIsNone(data['gran_formato'])
    
    def test_serialize_producto_gran_formato_with_nested(self):
        serializer = ProductoSerializer(instance=self.producto_gran_formato)
        data = serializer.data
        self.assertEqual(data['codigo'], "T002")
        self.assertIn('intervalos', data)
        self.assertIn('gran_formato', data)
        self.assertIn('inventarios', data)
        self.assertIsInstance(data['intervalos'], list)
        self.assertIsInstance(data['inventarios'], list)
        self.assertIsInstance(data['gran_formato'], dict)

    def test_deserialize_producto_with_nested(self):
        payload = {
            "codigo": "T002.0",
            "descripcion": "Tarjeta Nueva",
            "abreviado": "TarjN",
            "categoria": "S",
            "is_active": True,
            "intervalos": [
                {"desde": 5, "precio_con_iva": 100.0, "duplex": False}
            ],
            "inventarios": [
                {"inventario": self.inventario.id, "utiliza_inventario": 1.5}
            ]
        }
        serializer = ProductoSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        producto = serializer.save()
        self.assertEqual(producto.codigo, "T002.0")
        self.assertEqual(producto.intervalos.count(), 1)
        self.assertEqual(producto.inventarios.count(), 1)

        with self.assertRaises(Producto.gran_formato.RelatedObjectDoesNotExist):
            _ = producto.gran_formato
        
        # === Gran formato ===
        payload = {
            "codigo": "T003.0",
            "descripcion": "Lona Nueva",
            "abreviado": "Lona",
            "categoria": "G",
            "is_active": True,
            "gran_formato": {"min_m2": 1.0, "precio_m2": 200.0},
            "inventarios": [
                {"inventario": self.inventario.id, "utiliza_inventario": 1.5}
            ]
        }
        serializer = ProductoSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        producto = serializer.save()
        self.assertEqual(producto.codigo, "T003.0")
        self.assertIsNotNone(producto.gran_formato)
        self.assertEqual(producto.intervalos.count(), 0)
        self.assertEqual(producto.inventarios.count(), 1)

    def test_partial_update_producto(self):
        serializer = ProductoSerializer(instance=self.producto, data={"descripcion": "Tarjeta Actualizada"}, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        producto = serializer.save()
        self.assertEqual(producto.descripcion, "Tarjeta Actualizada")

    def test_invalid_gran_formato_for_simple_category(self):
        payload = {
            "codigo": "T003",
            "descripcion": "Lona2",
            "abreviado": "LonaTest2",
            "categoria": "S",
            "is_active": True,
            "gran_formato": {"min_m2": 1.0, "precio_m2": 200.0}
        }
        serializer = ProductoSerializer(data=payload)
        with self.assertRaises(ValueError):
            serializer.is_valid(raise_exception=True)
            serializer.save()
    
    def test_invalid_simple_for_gran_category(self):
        payload = {
            "codigo": "T005",
            "descripcion": "Impresiones",
            "abreviado": "Impresiones",
            "categoria": "G",
            "is_active": True,
            "intervalos": [
                {"desde": 5, "precio_con_iva": 100.0, "duplex": False}
            ]
        }
        serializer = ProductoSerializer(data=payload)
        with self.assertRaises(ValueError):
            serializer.is_valid(raise_exception=True)
            serializer.save()


class ProductoViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = Usuario.objects.create_user(username='testuser', password='testpass')
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
    
    def test_list_is_successful(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('producto-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)
    
    def test_detail_is_successful(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('producto-detail', args=[self.producto_simple.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['codigo'], self.producto_simple.codigo)

    def test_list_requires_auth(self):
        url = reverse('producto-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_precio_importe(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('producto-get-precio-importe', args=[self.producto_simple.id])
        data = {'cantidad': 20, 'descuento_unit': 1.0}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('precio_con_iva', response.data)
        self.assertIn('importe', response.data)

    def test_get_precio_importe_gran_formato(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('producto-get-precio-importe', args=[self.producto_gran_formato.id])
        data = {'ancho_producto': 2.0, 'alto_producto': 1.5, 'ancho_material': 1.0, 'descuento_unit': 5.0}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('precio_con_iva', response.data)
        self.assertIn('importe', response.data)

    def test_duplex_intervalos(self):
        self.client.force_authenticate(user=self.user)
        ProductoIntervalo.objects.create(
            producto=self.producto_simple,
            desde=101,
            precio_con_iva=150.0,
            duplex=False
        )
        ProductoIntervalo.objects.create(
            producto=self.producto_simple,
            desde=101,
            precio_con_iva=120.0,
            duplex=True
        )

        # Califica para precio duplex
        url = reverse('producto-get-precio-importe', args=[self.producto_simple.id])
        data = {'cantidad': 120, 'duplex': True, 'descuento_unit': 2.5}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['precio_con_iva'], 120.0)
        self.assertEqual(response.data['importe'], 120*(120.0 - 2.5))

        # No califica para precio duplex, usa el normal
        url = reverse('producto-get-precio-importe', args=[self.producto_simple.id])
        data = {'cantidad': 50, 'duplex': True, 'descuento_unit': 2.5}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['precio_con_iva'], 100.0)
        self.assertEqual(response.data['importe'], 50*(100.0 - 2.5))
    
    def test_sobrante_gran_formato(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('producto-get-precio-importe', args=[self.producto_gran_formato.id])
        data = {'ancho_producto': 1.0, 'alto_producto': 3, 'ancho_material': 2.0}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # El ancho del producto se ajusta al ancho del material
        self.assertEqual(response.data['precio_con_iva'], 200.0)
        self.assertEqual(response.data['importe'], 3.0*2.0*200.0)


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
