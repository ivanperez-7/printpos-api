from django.contrib import admin
from django.urls import path, include
from debug_toolbar.toolbar import debug_toolbar_urls

from system.views import CookieTokenObtainPairView, CookieTokenRefreshView, logout_view, me
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/token/', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/logout/', logout_view, name='logout'),
    path('api/v1/me/', me, name='me'),
    path('api/v1/organizacion/', include('organizacion.urls')),
    path('api/v1/productos/', include('productos.urls')),
    path('api/v1/movimientos/', include('movimiento.urls')),
    path('api/v1/system/', include('system.urls')),
]

admin.site.site_header = 'PrintPOS DB'
admin.site.site_title = 'PrintPOS DB'

if settings.DEBUG:
    urlpatterns += debug_toolbar_urls()
