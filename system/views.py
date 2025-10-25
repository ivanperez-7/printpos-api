from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        access = request.COOKIES.get('access')
        if not access:
            return None
        validated_token = self.get_validated_token(access)
        return self.get_user(validated_token), validated_token


@api_view()
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    return Response({'id': user.id, 'username': user.username})


@api_view(['POST'])
def verificar_credenciales_admin(request):
    """ Recibe JSON: { "username": "...", "password": "..." }
        Retorna 200 si las credenciales son correctas, 401 si no. """
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response({"detail": "Faltan datos"}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)

    if user is not None and user.is_manager:
        return Response({"detail": "Credenciales válidas"}, status=status.HTTP_200_OK)
    else:
        return Response({"detail": "Usuario no existe o no es staff"}, status=status.HTTP_401_UNAUTHORIZED)
