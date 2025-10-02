from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view()
@permission_classes([IsAuthenticated])
def get_tabla_precios_simples(request):
    return Response(data={'lol': 'lol'}, status=200)
