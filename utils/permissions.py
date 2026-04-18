from rest_framework.permissions import BasePermission


class HasValidBranch(BasePermission):
    def has_permission(self, request, view):
        branch_id = request.headers.get('x-branch-id')
        request.branch_id = branch_id

        return (
            request.user
            and request.user.is_authenticated
            and branch_id
            and request.user.profile.sucursales.filter(id=branch_id, activo=True).exists()
        )
