import os
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate
from django.middleware.csrf import get_token
from django.urls import reverse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


class CookieTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            data = response.data
            refresh = data.pop('refresh', None)

            if refresh:
                response.set_cookie(
                    key='refresh_token',
                    value=refresh,
                    httponly=True,
                    secure=not settings.DEBUG,
                    samesite='Lax' if settings.DEBUG else 'None',
                    path=reverse('token_refresh'),
                    max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
                )
                
            csrf_token = get_token(request)
            response.set_cookie(
                key='csrftoken',
                value=csrf_token,
                httponly=False,
                secure=not settings.DEBUG,
                samesite='Lax' if settings.DEBUG else 'None'
            )
        return response


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh = request.COOKIES.get('refresh_token')

        if refresh is None:
            return Response({'detail': 'Refresh token not found.'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.get_serializer(data={'refresh': refresh})
        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    response = Response({'detail': 'Sesión cerrada correctamente.'}, status=status.HTTP_200_OK)
    response.delete_cookie(key='refresh_token')
    return response


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
