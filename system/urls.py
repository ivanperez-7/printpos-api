from django.urls import path

from .views import verificar_credenciales_admin


urlpatterns = [
    path('verificar-admin', verificar_credenciales_admin, name='verificar-admin'),
]
