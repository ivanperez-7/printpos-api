from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import Venta, VentaDetallado
from clientes.models import Cliente
from inventario.models import Producto, Inventario
from pagos.models import MetodoPago, VentaPago


class VentaModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.cliente = Cliente.objects.create(nombre='Cliente Test')
        self.producto = Producto.objects.create(descripcion='Producto Test')
        self.venta = Venta.objects.create(
            cliente=self.cliente,
            vendedor=self.user,
            comentarios='Comentario',
            estado='No terminada',
            is_active=True
        )
        self.metodo_pago = MetodoPago.objects.create(metodo='Efectivo')
        VentaDetallado.objects.create(
            venta=self.venta,
            producto=self.producto,
            cantidad=4,
            precio=10,
            descuento=0
        )
        VentaPago.objects.create(
            venta=self.venta,
            metodo_pago=self.metodo_pago,
            monto=40.00000124892,
            usuario=self.user
        )


    def test_str_representation(self):
        self.assertIn(f"Venta #{self.venta.id}", str(self.venta))

    def test_unique_active_venta_per_user(self):
        with self.assertRaises(ValueError):
            Venta.objects.create(
                cliente=self.cliente,
                vendedor=self.user,
                is_active=True
            )
    
    def test_cancelar_venta(self):
        self.venta.cancelar()
        self.venta.refresh_from_db()
        self.assertEqual(self.venta.estado, 'Cancelada')
        self.assertFalse(self.venta.is_active)
        self.assertEqual(self.venta.pagos.count(), 2)  # Original pago + devolución
        
        devolucion = self.venta.pagos.latest('pk')
        self.assertEqual(devolucion.monto, -40)


class VentaDetalladoModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.cliente = Cliente.objects.create(nombre='Cliente Test')
        self.producto = Producto.objects.create(descripcion='Producto Test')
        self.inventario = Inventario.objects.create(
            nombre='Inventario Test', tamano_lote=500, precio_lote=100, minimo_lotes=1, unidades_restantes=800
        )
        self.producto.inventarios.create(inventario=self.inventario, utiliza_inventario=1)

        self.venta = Venta.objects.create(
            cliente=self.cliente,
            vendedor=self.user,
            is_active=False
        )

    def test_str_representation(self):
        detalle = VentaDetallado.objects.create(
            venta=self.venta,
            producto=self.producto,
            cantidad=1,
            precio=10,
            descuento=0
        )
        self.assertIn(f"Detalle de Venta #{self.venta.id}", str(detalle))

    def test_importe_property_not_implemented(self):
        detalle = VentaDetallado.objects.create(
            venta=self.venta,
            producto=self.producto,
            cantidad=1,
            precio=10,
            descuento=0
        )
        with self.assertRaises(NotImplementedError):
            _ = detalle.importe
    
    def test_substract_inventory_on_save(self):
        VentaDetallado.objects.create(
            venta=self.venta,
            producto=self.producto,
            cantidad=3,
            precio=10,
            descuento=0
        )
        self.inventario.refresh_from_db()
        self.assertEqual(self.inventario.unidades_restantes, 797)
    
    def test_add_inventory_on_cancel(self):
        VentaDetallado.objects.create(
            venta=self.venta,
            producto=self.producto,
            cantidad=4,
            precio=10,
            descuento=0
        )
        self.venta.cancelar()
        self.inventario.refresh_from_db()
        self.assertEqual(self.inventario.unidades_restantes, 800)


class VentaViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.cliente = Cliente.objects.create(nombre='Cliente Test')
        self.venta = Venta.objects.create(
            cliente=self.cliente,
            vendedor=self.user,
            estado='Recibido $150.00',
            is_active=True
        )
        self.client.force_authenticate(user=self.user)

    def test_create_venta_returns_existing_if_active(self):
        url = reverse('venta-list')
        data = {
            'cliente': self.cliente.id,
            'is_active': True
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], self.venta.id)

    def test_finalizar_action_changes_estado(self):
        url = reverse('venta-finalizar', args=[self.venta.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.venta.refresh_from_db()
        self.assertEqual(self.venta.estado, 'Terminada')

    def test_finalizar_action_invalid_estado(self):
        self.venta.estado = 'Terminada'
        self.venta.save()
        url = reverse('venta-finalizar', args=[self.venta.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)
        self.assertIn('detail', response.data)
    
    def test_save_progress_action(self):
        new_user = User.objects.create_user(username='newuser', password='pass')
        venta = Venta.objects.create(
            cliente=self.cliente,
            vendedor=new_user,
            estado='No terminada',
            is_active=True
        )
        url = reverse('venta-detail', args=[venta.id])
        data = {
            'comentarios': 'Nuevos comentarios',
            'detalles': [
                {
                    'cantidad': 1255.0,
                    'precio': 0.70,
                    'descuento': 0.00,
                    'especificaciones': 'EJEMPLO DE ESPECIFICACIONES',
                    'producto': Producto.objects.create(descripcion='Otro Producto').id
                }
            ]
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        venta.refresh_from_db()
        self.assertEqual(venta.comentarios, 'Nuevos comentarios')
        self.assertEqual(venta.detalles.count(), 1)


class GetUsuarioPendientesTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.cliente = Cliente.objects.create(nombre='Cliente Test')
        self.venta = Venta.objects.create(
            cliente=self.cliente,
            vendedor=self.user,
            estado='Recibido $150.00',
            is_active=True
        )
        self.client.force_authenticate(user=self.user)

    def test_get_usuario_pendientes_count(self):
        url = reverse('get-usuario-pendientes')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('count', response.data)
