from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/clientes/', include('clientes.urls')),
    path('api/v1/productos/', include('inventario.urls')),
    path('api/v1/ventas/', include('ventas.urls')),
    path('api/v1/pagos/', include('pagos.urls')),
    path('api/v1/system/', include('system.urls'))
]

admin.site.site_header = "PrintPOS DB"
admin.site.site_title = "PrintPOS DB"
