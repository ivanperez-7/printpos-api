from django.urls import path

from .views import *


urlpatterns = [
    path('get-tabla-precios-simples/', get_tabla_precios_simples),
]
