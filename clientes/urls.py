from django.urls import path

from .views import *


urlpatterns = [
    path('get-tabla-clientes/', get_tabla_clientes),
]
