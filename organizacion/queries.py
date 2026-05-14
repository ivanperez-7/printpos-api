from .models import Cliente


def clientes_queryset(branch_id: int):
    return Cliente.objects.filter(activo=True, sucursal=branch_id)
