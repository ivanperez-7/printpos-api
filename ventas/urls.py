from django.urls import path

from .views import *


urlpatterns = [
    path('get-usuario-pendientes/', get_usuario_pendientes),
]
