from django.contrib import admin
from django.urls import path, include

from system.views import CookieTokenObtainPairView, CookieTokenRefreshView, logout_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/token/', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/logout/', logout_view, name='logout'),
    path('api/v1/productos/', include('productos.urls')),
    path('api/v1/movimientos/', include('movimiento.urls')),
]

admin.site.site_header = "PrintPOS DB"
admin.site.site_title = "PrintPOS DB"
