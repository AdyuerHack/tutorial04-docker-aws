from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from tienda_app.infra.factories import PaymentFactory
from tienda_app.models import Libro
from tienda_app.services import CompraService

from .serializers import LibroSerializer, OrdenInputSerializer


class LibroListAPIView(APIView):
    """
    Endpoint para listar todos los libros y su stock actual vía JSON.
    GET /api/v1/libros/
    """

    def get(self, request):
        libros = Libro.objects.all()
        serializer = LibroSerializer(libros, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CompraAPIView(APIView):
    """
    Endpoint para procesar compras vía JSON.
    POST /api/v1/comprar/
    Payload: {"libro_id": 1, "direccion_envio": "Calle 123", "cantidad": 1}
    """

    def get(self, request):
        """
        Documentación interactiva y especificación del endpoint para la interfaz de DRF.
        """
        return Response(
            {
                "mensaje": "Endpoint para procesar compras vía API REST (JSON).",
                "metodo_permitido": "POST",
                "ejemplo_payload": {
                    "libro_id": 1,
                    "direccion_envio": "Carrera 7 # 45-20, Bogotá",
                    "cantidad": 1,
                },
                "documentacion": "Envíe un POST con el payload requerido para ejecutar la orden en el Service Layer.",
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        # 1. Validación de datos de entrada (Adapter / DTO)
        serializer = OrdenInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        datos = serializer.validated_data

        try:
            # 2. Inyección de Dependencias (Factory Method)
            gateway = PaymentFactory.get_processor()

            # 3. Ejecución de Lógica de Negocio (Service Layer reutilizado)
            servicio = CompraService(procesador_pago=gateway)
            usuario = request.user if request.user and request.user.is_authenticated else None

            # Noten como el servicio NO cambia, solo cambia quien lo llama
            resultado = servicio.ejecutar_compra(
                libro_id=datos['libro_id'],
                cantidad=datos.get('cantidad', 1),
                direccion=datos['direccion_envio'],
                usuario=usuario,
            )

            return Response(
                {
                    "estado": "exito",
                    "mensaje": f"Orden creada. Total: {resultado}",
                },
                status=status.HTTP_201_CREATED,
            )

        except ValueError as e:
            # Errores de negocio (ej: Sin stock o datos insuficientes)
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)
        except Exception as e:
            # Errores inesperados o fallos de infraestructura
            return Response({"error": "Error interno", "detalle": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
