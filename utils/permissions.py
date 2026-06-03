from rest_framework.permissions import BasePermission


class HasValidBranch(BasePermission):
    def has_permission(self, request, view):
        branch_id = request.headers.get('x-branch-id')
        request.branch_id = branch_id

        if not request.user or not request.user.is_authenticated or not branch_id:
            return False
        if not hasattr(request.user, 'profile'):
            return False
        return request.user.profile.sucursales.filter(id=branch_id, activo=True).exists()


class HasAdminRole(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, 'profile')
            and request.user.profile.rol == 'admin'
        )
