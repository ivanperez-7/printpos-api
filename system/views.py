from django.conf import settings
from django.middleware.csrf import get_token
from django.urls import reverse
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import ConfiguracionSistema
from .serializers import ConfiguracionSistemaSerializer


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
    response.set_cookie(
        key='refresh_token',
        value='',
        httponly=True,
        secure=not settings.DEBUG,
        samesite='Lax' if settings.DEBUG else 'None',
        path=reverse('token_refresh'),
    )
    return response


class ConfiguracionSistemaViewSet(viewsets.ModelViewSet):
    queryset = ConfiguracionSistema.objects.all()
    serializer_class = ConfiguracionSistemaSerializer
