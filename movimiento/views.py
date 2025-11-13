from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import EntradaInventario, SalidaInventario
from .serializers import EntradaInventarioSerializer, SalidaInventarioSerializer

__all__ = [
    'EntradaInventarioViewSet',
    'SalidaInventarioViewSet',
    'main_movements_table'
]


class EntradaInventarioViewSet(viewsets.ModelViewSet):
    queryset = EntradaInventario.objects.all()
    serializer_class = EntradaInventarioSerializer


class SalidaInventarioViewSet(viewsets.ModelViewSet):
    queryset = SalidaInventario.objects.all()
    serializer_class = SalidaInventarioSerializer


@api_view(['GET'])
def main_movements_table(request):
    '''
    Vista para obtener los datos combinados de entradas y salidas de inventario
    para mostrar en una tabla principal.
    '''
    entradas = EntradaInventario.objects.all()
    salidas = SalidaInventario.objects.all()

    entrada_serializer = EntradaInventarioSerializer(entradas, many=True)
    salida_serializer = SalidaInventarioSerializer(salidas, many=True)

    combined_data = {
        'entradas': entrada_serializer.data,
        'salidas': salida_serializer.data,
    }
    return Response(combined_data)
