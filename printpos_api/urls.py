from django.contrib import admin
from django.contrib.auth.models import User
from django.urls import path, include

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super(CustomTokenObtainPairSerializer, self).validate(attrs)
        return {
            'token': data['access'],
            'username': attrs['username'],
            'is_admin': User.objects.get(username=attrs['username']).is_staff
        }


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/token/', CustomTokenObtainPairView.as_view()),
    path('api/v1/clientes/', include('clientes.urls')),
    path('api/v1/productos/', include('inventario.urls')),
    path('api/v1/ventas/', include('ventas.urls'))
]

admin.site.site_header = "PrintPOS DB"
admin.site.site_title = "PrintPOS DB"
