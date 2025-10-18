from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(['POST'])
def verificar_credenciales_admin(request):
    """ Recibe JSON: { "username": "...", "password": "..." }
        Retorna 200 si las credenciales son correctas, 401 si no. """
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response({"detail": "Faltan datos"}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)

    if user is not None and user.is_staff:
        return Response({"detail": "Credenciales válidas"}, status=status.HTTP_200_OK)
    else:
        return Response({"detail": "Usuario no existe o no es staff"}, status=status.HTTP_401_UNAUTHORIZED)
