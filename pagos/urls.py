from django.urls import path, include
from rest_framework import routers

from .views import *


router = routers.DefaultRouter()
router.register('cajas', CajaViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('get-all-movimientos-caja', get_all_movimientos_caja, name='get-all-movimientos-caja'),
    path('generate-report-pdf', generate_report_pdf, name='generate-report-pdf'),
]
