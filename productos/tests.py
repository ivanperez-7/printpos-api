from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from movimiento.models import Movimiento, MovimientoItem
from organizacion.models import Cliente, EquipoCliente, PerfilUsuario, Sucursal
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
            cantidad_inicial=100
        )
        self.assertEqual(str(lote), "L001")


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
            cantidad_inicial=50
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
            cantidad_inicial=200
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
            cantidad_inicial=30
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
        self.sucursal = Sucursal.objects.create(nombre="Sucursal Test")

    def test_list(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        PerfilUsuario.objects.create(usuario=user, rol='admin')
        user.profile.sucursales.add(self.sucursal)
        self.client.force_login(user)

        url = reverse('producto-list')
        response = self.client.get(url, HTTP_X_BRANCH_ID=self.sucursal.id)
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
            cantidad_inicial=60
        )
        self.sucursal = Sucursal.objects.create(nombre="Sucursal Test 2")

    def test_list(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        PerfilUsuario.objects.create(usuario=user, rol='admin')
        user.profile.sucursales.add(self.sucursal)
        self.client.force_login(user)

        url = reverse('lote-list')
        response = self.client.get(url, HTTP_X_BRANCH_ID=self.sucursal.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['codigo_lote'], "L005")


# ── Additional Product Model Tests ────────────────────────────────────


class ProductoModelSaveTest(APITestCase):
    def test_save_rejects_inactive_with_movements(self):
        categoria = Categoría.objects.create(nombre="Consumibles")
        proveedor = Proveedor.objects.create(nombre="Prov Save")
        producto = Producto.objects.create(
            codigo_interno="P-SAVE",
            descripcion="Test",
            categoria=categoria,
            unidad_medida="pieza",
            sku="SKU-SAVE",
            min_stock=5,
            proveedor=proveedor,
        )
        user = User.objects.create_user(username='saveuser', password='pass')
        movimiento = Movimiento.objects.create(tipo='entrada', creado_por=user)
        MovimientoItem.objects.create(movimiento=movimiento, producto=producto, cantidad=1)

        with self.assertRaises(ValueError):
            producto.status = 'inactivo'
            producto.save()

    def test_save_allows_inactive_without_movements(self):
        categoria = Categoría.objects.create(nombre="Consumibles2")
        proveedor = Proveedor.objects.create(nombre="Prov Save2")
        producto = Producto.objects.create(
            codigo_interno="P-SAFE",
            descripcion="Test Safe",
            categoria=categoria,
            unidad_medida="pieza",
            sku="SKU-SAFE",
            min_stock=5,
            proveedor=proveedor,
        )
        producto.status = 'inactivo'
        producto.save()
        producto.refresh_from_db()
        self.assertEqual(producto.status, 'inactivo')


# ── EquipoViewSet Custom Actions ──────────────────────────────────────


class EquipoViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='euser', password='pass')
        self.sucursal = Sucursal.objects.create(nombre='Suc Equipo')
        PerfilUsuario.objects.create(usuario=self.user, rol='admin')
        self.user.profile.sucursales.add(self.sucursal)
        self.client.force_login(self.user)
        self.marca = Marca.objects.create(nombre='Marca E')
        self.equipo = Equipo.objects.create(nombre='EQ-TEST', marca=self.marca)
        self.headers = {'HTTP_X_BRANCH_ID': self.sucursal.id}

    def test_clientes_action(self):
        cliente = Cliente.objects.create(nombre='Cli Eq', sucursal=self.sucursal)
        EquipoCliente.objects.create(
            equipo=self.equipo, cliente=cliente, alias='Alias1', contador_uso=100
        )
        url = reverse('equipo-clientes', kwargs={'pk': self.equipo.pk})
        response = self.client.get(url, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_stats_action(self):
        cliente = Cliente.objects.create(nombre='Cli Stats', sucursal=self.sucursal)
        EquipoCliente.objects.create(
            equipo=self.equipo, cliente=cliente, alias='Stats1', contador_uso=200
        )
        url = reverse('equipo-stats', kwargs={'pk': self.equipo.pk})
        response = self.client.get(url, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_instalaciones', response.data)
        self.assertIn('uso_total', response.data)


# ── Dashboard ─────────────────────────────────────────────────────────


class DashboardViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='duser', password='pass')
        self.sucursal = Sucursal.objects.create(nombre='Suc Dash')
        PerfilUsuario.objects.create(usuario=self.user, rol='admin')
        self.user.profile.sucursales.add(self.sucursal)
        self.client.force_login(self.user)
        self.headers = {'HTTP_X_BRANCH_ID': self.sucursal.id}

    def test_dashboard_returns_expected_keys(self):
        response = self.client.get('/api/v1/productos/dashboard/', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('stats', response.data)
        self.assertIn('categoriasChart', response.data)
        self.assertIn('movimientosChart', response.data)
        self.assertIn('topProductosChart', response.data)
        self.assertIn('productosBajos', response.data)

    def test_dashboard_stats_include_zero_counts(self):
        response = self.client.get('/api/v1/productos/dashboard/', **self.headers)
        stats = response.data['stats']
        self.assertEqual(stats['productos'], 0)
        self.assertEqual(stats['lotes'], 0)
        self.assertEqual(stats['categorias'], 0)
        self.assertEqual(stats['proveedores'], 0)
        self.assertEqual(stats['clientes'], 0)


# ── Additional ViewSet CRUD Tests ─────────────────────────────────────


class UnidadViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='uuser', password='pass')
        self.sucursal = Sucursal.objects.create(nombre='Suc Unidad')
        PerfilUsuario.objects.create(usuario=self.user, rol='admin')
        self.user.profile.sucursales.add(self.sucursal)
        self.client.force_login(self.user)
        self.headers = {'HTTP_X_BRANCH_ID': self.sucursal.id}
        cat = Categoría.objects.create(nombre='Cat Unidad')
        prov = Proveedor.objects.create(nombre='Prov Unidad')
        self.producto = Producto.objects.create(
            codigo_interno='P-UNI', descripcion='Test', categoria=cat,
            unidad_medida='pieza', sku='SKU-UNI', min_stock=1, proveedor=prov,
        )
        self.lote = Lote.objects.create(producto=self.producto, codigo_lote='L-UNI', cantidad_inicial=5)
        self.unidad = Unidad.objects.create(lote=self.lote)

    def test_list(self):
        url = reverse('unidad-list')
        response = self.client.get(url, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve(self):
        url = reverse('unidad-detail', kwargs={'pk': self.unidad.pk})
        response = self.client.get(url, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create(self):
        url = reverse('unidad-list')
        data = {'lote': self.lote.pk}
        response = self.client.post(url, data, format='json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class CategoriaViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cuser', password='pass')
        self.sucursal = Sucursal.objects.create(nombre='Suc Cat')
        PerfilUsuario.objects.create(usuario=self.user, rol='admin')
        self.user.profile.sucursales.add(self.sucursal)
        self.client.force_login(self.user)
        self.headers = {'HTTP_X_BRANCH_ID': self.sucursal.id}
        self.categoria = Categoría.objects.create(nombre='Cat ViewSet')

    def test_list(self):
        url = reverse('categoría-list')
        response = self.client.get(url, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create(self):
        url = reverse('categoría-list')
        data = {'nombre': 'Nueva Cat'}
        response = self.client.post(url, data, format='json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class MarcaViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='muser', password='pass')
        self.sucursal = Sucursal.objects.create(nombre='Suc Marca')
        PerfilUsuario.objects.create(usuario=self.user, rol='admin')
        self.user.profile.sucursales.add(self.sucursal)
        self.client.force_login(self.user)
        self.headers = {'HTTP_X_BRANCH_ID': self.sucursal.id}
        self.marca = Marca.objects.create(nombre='Marca VS')

    def test_list(self):
        url = reverse('marca-list')
        response = self.client.get(url, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create(self):
        url = reverse('marca-list')
        data = {'nombre': 'Nueva Marca'}
        response = self.client.post(url, data, format='json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class ProveedorViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='puser', password='pass')
        self.sucursal = Sucursal.objects.create(nombre='Suc Prov')
        PerfilUsuario.objects.create(usuario=self.user, rol='admin')
        self.user.profile.sucursales.add(self.sucursal)
        self.client.force_login(self.user)
        self.headers = {'HTTP_X_BRANCH_ID': self.sucursal.id}
        self.proveedor = Proveedor.objects.create(nombre='Prov VS')

    def test_list(self):
        url = reverse('proveedor-list')
        response = self.client.get(url, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create(self):
        url = reverse('proveedor-list')
        data = {'nombre': 'Nuevo Prov'}
        response = self.client.post(url, data, format='json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
