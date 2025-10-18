from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase

from .models import MetodoPago, Caja, VentaPago
from .pdf import generar_corte_pdf
from clientes.models import Cliente
from organizacion.models import Usuario
from ventas.models import Venta


class CajaModelTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(username="testuser", password="pass")
        self.metodo = MetodoPago.objects.create(metodo="Tarjeta", comision_porcentaje=Decimal("1.00"))

    def test_str(self):
        caja = Caja.objects.create(
            monto=Decimal("100.00"),
            metodo_pago=self.metodo,
            usuario=self.user,
            descripcion="Ingreso"
        )
        self.assertIn("Movimiento", str(caja))
        self.assertIn("100.00", str(caja))
        self.assertIn("Tarjeta", str(caja))


class CajaViewSetTest(APITestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(username="apiuser", password="pass")
        self.metodo = MetodoPago.objects.create(metodo="Efectivo", comision_porcentaje=Decimal("0.00"))
        Caja.objects.create(
            monto=Decimal("50.00"),
            metodo_pago=self.metodo,
            usuario=self.user,
            descripcion="Apertura"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_caja_movement(self):
        url = reverse("caja-list")
        data = {
            "monto": "75",
            "metodo_pago": self.metodo.id,
            "usuario": self.user.id,
            "descripcion": "Test"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Caja.objects.count(), 2)
        movimiento = Caja.objects.get(id=response.data['id'])
        self.assertEqual(movimiento.monto, Decimal("75.00"))
        self.assertEqual(movimiento.metodo_pago, self.metodo)
        self.assertEqual(movimiento.usuario, self.user)
        self.assertEqual(movimiento.descripcion, "Test")


class VentaPagoModelTest(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(nombre="Cliente Test")
        self.user = Usuario.objects.create_user(username="testuser", password="pass")
        self.metodo = MetodoPago.objects.create(metodo="Transferencia", comision_porcentaje=Decimal("0.00"))
        self.venta = Venta.objects.create(cliente=self.cliente, vendedor=self.user, estado="No terminada", is_active=True)

    def test_str(self):
        pago = VentaPago.objects.create(
            venta=self.venta,
            metodo_pago=self.metodo,
            monto=Decimal("200.00"),
            usuario=self.user
        )
        self.assertIn("Pago #", str(pago))
        self.assertIn("Venta", str(pago))
        self.assertIn("Transferencia", str(pago))
    
    def test_descripcion_annotation(self):
        pago = VentaPago.objects.create(
            venta=self.venta,
            metodo_pago=self.metodo,
            monto=Decimal("200.00"),
            usuario=self.user
        )
        pago_devolucion = VentaPago.objects.create(
            venta=self.venta,
            metodo_pago=self.metodo,
            monto=Decimal("-50.00"),
            usuario=self.user
        )
        pagos = VentaPago.objects.con_descripcion().filter(id__in=[pago.id, pago_devolucion.id])
        for p in pagos:
            if p.id == pago.id:
                self.assertEqual(p.descripcion, f"Pago de venta con folio {self.venta.id}")
            elif p.id == pago_devolucion.id:
                self.assertEqual(p.descripcion, f"Devolución de venta con folio {self.venta.id}")


class PagosViewsTest(APITestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(nombre="Cliente Test")
        self.user = Usuario.objects.create_user(username="apiuser", password="pass")
        self.metodo = MetodoPago.objects.create(metodo="Efectivo", comision_porcentaje=Decimal("0.00"))
        self.venta = Venta.objects.create(cliente=self.cliente, vendedor=self.user, estado="No terminada", is_active=True)
        Caja.objects.create(
            monto=Decimal("-50.00"),
            metodo_pago=self.metodo,
            usuario=self.user,
            descripcion="Renta"
        )
        Caja.objects.create(
            monto=Decimal("50.00"),
            metodo_pago=self.metodo,
            usuario=self.user,
            descripcion="Apertura",
            fecha_hora=timezone.now() - timezone.timedelta(days=10)
        )
        VentaPago.objects.create(
            venta=self.venta,
            metodo_pago=self.metodo,
            monto=Decimal("150.00"),
            usuario=self.user
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_all_movimientos_caja(self):
        url = reverse("get-all-movimientos-caja")
        data = {
            "fecha_inicio": (timezone.now() - timezone.timedelta(days=5)).date().isoformat(),
            "fecha_fin": (timezone.now() + timezone.timedelta(days=1)).date().isoformat(),
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertTrue(any("descripcion" in m for m in response.data))

        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

    def test_generate_report_pdf(self):
        url = reverse("generate-report-pdf")
        data = {
            "fecha_inicio": (timezone.now() - timezone.timedelta(days=5)).date().isoformat(),
            "fecha_fin": (timezone.now() + timezone.timedelta(days=1)).date().isoformat(),
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8')
        self.assertTrue(len(response.content) > 0)

        # test without date filters raises error
        response = self.client.post(url)
        self.assertEqual(response.status_code, 500)


class PdfTest(TestCase):
    def test_generar_corte_pdf(self):
        metodo = MetodoPago.objects.create(metodo="Efectivo", comision_porcentaje=Decimal("0.00"))
        user = Usuario.objects.create_user(username="pdfuser", password="pass")
        venta = Venta.objects.create(
            cliente=Cliente.objects.create(nombre="Cliente Test"), vendedor=user, estado="No terminada", is_active=True
        )

        VentaPago.objects.create(
            venta=venta,
            metodo_pago=metodo,
            monto=Decimal("150.00"),
            usuario=user
        )
        VentaPago.objects.create(
            venta=venta,
            metodo_pago=metodo,
            monto=Decimal("350.00"),
            usuario=user
        )

        Caja.objects.create(
            monto=Decimal("100.00"),
            metodo_pago=metodo,
            usuario=user,
            descripcion="Ingreso prueba"
        )
        Caja.objects.create(
            monto=Decimal("-50.00"),
            metodo_pago=metodo,
            usuario=user,
            descripcion="Egreso prueba"
        )

        pdf_buffer = generar_corte_pdf(Caja.objects.union(VentaPago.objects.all()), responsable=user.username)
        self.assertTrue(pdf_buffer.getbuffer().nbytes > 0)
