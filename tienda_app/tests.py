import io
import os
from contextlib import redirect_stdout
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from .domain.builders import OrdenBuilder
from .infra.factories import PaymentFactory, MockPaymentProcessor
from .infra.gateways import BancoNacionalProcesador
from .models import Libro, Inventario, Orden
from .services import CompraService

User = get_user_model()


class PaymentFactoryTests(TestCase):
    def test_default_factory_returns_banco_nacional(self):
        if 'PAYMENT_PROVIDER' in os.environ:
            del os.environ['PAYMENT_PROVIDER']
        processor = PaymentFactory.get_processor()
        self.assertIsInstance(processor, BancoNacionalProcesador)

    def test_mock_factory_returns_mock_processor(self):
        os.environ['PAYMENT_PROVIDER'] = 'MOCK'
        try:
            processor = PaymentFactory.get_processor()
            self.assertIsInstance(processor, MockPaymentProcessor)
        finally:
            del os.environ['PAYMENT_PROVIDER']

    def test_mock_payment_processor_execution(self):
        processor = MockPaymentProcessor()
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            resultado = processor.pagar(184.45)

        self.assertTrue(resultado)
        output = buffer.getvalue()
        self.assertIn("[DEBUG] Mock Payment: Procesando pago de $184.45 sin cargo real.", output)


class OrdenBuilderTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username='estudiante_test')
        self.libro = Libro.objects.create(titulo='Libro Patrones Creacionales', precio=Decimal('100.00'))

    def test_builder_fluent_interface_and_iva_calculation(self):
        builder = OrdenBuilder()
        orden = (
            builder
            .con_usuario(self.usuario)
            .con_productos([self.libro])
            .para_envio("Carrera 7 # 45-10")
            .build()
        )

        self.assertIsNotNone(orden.id)
        self.assertEqual(orden.usuario, self.usuario)
        self.assertEqual(orden.libro, self.libro)
        self.assertEqual(orden.direccion_envio, "Carrera 7 # 45-10")
        # 100 * 1.19 = 119.00
        self.assertEqual(orden.total, Decimal('119.00'))

    def test_builder_raises_error_when_no_products(self):
        builder = OrdenBuilder()
        builder.con_usuario(self.usuario)
        with self.assertRaises(ValueError):
            builder.build()


class CompraServiceTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username='comprador_service')
        self.libro = Libro.objects.create(titulo='Arquitectura Limpia', precio=Decimal('50.00'))
        self.inventario = Inventario.objects.create(libro=self.libro, cantidad=5)

    def test_ejecutar_proceso_compra_con_mock(self):
        processor = MockPaymentProcessor()
        servicio = CompraService(procesador_pago=processor)
        resultado = servicio.ejecutar_proceso_compra(
            usuario=self.usuario,
            lista_productos=[self.libro],
            direccion="Calle 100",
        )
        self.assertIn("procesada exitosamente", resultado)

    def test_ejecutar_compra_web_flow(self):
        os.environ['PAYMENT_PROVIDER'] = 'MOCK'
        try:
            processor = PaymentFactory.get_processor()
            servicio = CompraService(procesador_pago=processor)
            total = servicio.ejecutar_compra(libro_id=self.libro.id, cantidad=1)
            # 50.00 * 1.19 = 59.50
            self.assertEqual(total, Decimal('59.50'))
            self.inventario.refresh_from_db()
            self.assertEqual(self.inventario.cantidad, 4)
        finally:
            del os.environ['PAYMENT_PROVIDER']


class CompraViewIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.libro = Libro.objects.create(titulo='Django Enterprise', precio=Decimal('200.00'))
        self.inventario = Inventario.objects.create(libro=self.libro, cantidad=10)

    def test_post_compra_view_with_mock_environment(self):
        os.environ['PAYMENT_PROVIDER'] = 'MOCK'
        try:
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                response = self.client.post(reverse('finalizar_compra', args=[self.libro.id]))

            self.assertEqual(response.status_code, 200)
            self.assertIn('¡Gracias por su compra!', response.content.decode('utf-8'))
            self.assertIn("[DEBUG] Mock Payment:", buffer.getvalue())
        finally:
            del os.environ['PAYMENT_PROVIDER']


class Tutorial03APITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.libro = Libro.objects.create(titulo='Microservicios y APIs Limpias', precio=Decimal('100.00'))
        self.inventario = Inventario.objects.create(libro=self.libro, cantidad=5)

    def test_libro_serializer_includes_stock_actual(self):
        from .api.serializers import LibroSerializer
        serializer = LibroSerializer(self.libro)
        data = serializer.data
        self.assertEqual(data['id'], self.libro.id)
        self.assertEqual(data['titulo'], 'Microservicios y APIs Limpias')
        self.assertEqual(data['precio'], '100.00')
        self.assertEqual(data['stock_actual'], 5)

    def test_api_comprar_success(self):
        payload = {
            "libro_id": self.libro.id,
            "direccion_envio": "Calle 100 # 15-20, Bogotá",
            "cantidad": 2,
        }
        response = self.client.post(
            reverse('api_comprar'),
            data=payload,
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        res_data = response.json()
        self.assertEqual(res_data['estado'], 'exito')
        # 100 * 2 = 200 * 1.19 = 238.00
        self.assertIn('238.00', res_data['mensaje'])

        # Validacion de efectos colaterales (Persistencia)
        self.inventario.refresh_from_db()
        self.assertEqual(self.inventario.cantidad, 3)
        self.assertEqual(Orden.objects.filter(libro=self.libro).count(), 1)

    def test_api_comprar_sin_stock_retorna_409(self):
        payload = {
            "libro_id": self.libro.id,
            "direccion_envio": "Avenida Siempre Viva 742",
            "cantidad": 10,  # Solo hay 5
        }
        response = self.client.post(
            reverse('api_comprar'),
            data=payload,
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 409)
        self.assertIn('error', response.json())
        self.inventario.refresh_from_db()
        self.assertEqual(self.inventario.cantidad, 5)

    def test_api_comprar_datos_invalidos_retorna_400(self):
        payload = {
            # Falta libro_id
            "direccion_envio": "Calle Invalida",
        }
        response = self.client.post(
            reverse('api_comprar'),
            data=payload,
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('libro_id', response.json())

    def test_api_libros_list(self):
        response = self.client.get(reverse('api_libros'))
        self.assertEqual(response.status_code, 200)
        libros = response.json()
        self.assertTrue(len(libros) >= 1)
        self.assertEqual(libros[0]['stock_actual'], 5)

    def test_cross_validation_api_purchase_reflects_in_html_view(self):
        # 1. Consulta inicial en la vista HTML
        resp_html_inicial = self.client.get(reverse('inventario_html'))
        self.assertEqual(resp_html_inicial.status_code, 200)
        self.assertIn('5 unidades', resp_html_inicial.content.decode('utf-8'))

        # 2. Compra realizada exclusivamente vía API REST
        payload = {
            "libro_id": self.libro.id,
            "direccion_envio": "Transversal 45 # 10-20",
            "cantidad": 1,
        }
        resp_api = self.client.post(
            reverse('api_comprar'),
            data=payload,
            content_type='application/json',
        )
        self.assertEqual(resp_api.status_code, 201)

        # 3. La vista HTML ahora debe reflejar automáticamente el nuevo inventario (4 unidades)
        resp_html_posterior = self.client.get(reverse('inventario_html'))
        self.assertEqual(resp_html_posterior.status_code, 200)
        self.assertIn('4 unidades', resp_html_posterior.content.decode('utf-8'))
