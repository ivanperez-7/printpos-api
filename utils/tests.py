from django.contrib.auth.models import User, AnonymousUser
from django.test import TestCase, RequestFactory

from organizacion.models import PerfilUsuario, Sucursal
from utils.permissions import HasValidBranch


class HasValidBranchTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.permission = HasValidBranch()
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.sucursal = Sucursal.objects.create(nombre='Sucursal A')
        PerfilUsuario.objects.create(usuario=self.user, rol='admin')
        self.user.profile.sucursales.add(self.sucursal)
        self.view = object()

    def _make_request(self, user=None, branch_id=None):
        headers = {}
        if branch_id is not None:
            headers['HTTP_X_BRANCH_ID'] = str(branch_id)
        request = self.factory.get('/', **headers)
        request.user = user or self.user
        return request

    def test_allows_valid_branch(self):
        request = self._make_request(branch_id=self.sucursal.id)
        result = self.permission.has_permission(request, self.view)
        self.assertTrue(result)
        self.assertEqual(request.branch_id, str(self.sucursal.id))

    def test_rejects_anonymous_user(self):
        request = self._make_request(user=AnonymousUser(), branch_id=self.sucursal.id)
        result = self.permission.has_permission(request, self.view)
        self.assertFalse(result)

    def test_rejects_missing_branch_header(self):
        request = self._make_request(branch_id=None)
        result = self.permission.has_permission(request, self.view)
        self.assertFalse(result)

    def test_rejects_user_without_profile(self):
        no_profile_user = User.objects.create_user(username='noprofile', password='pass')
        request = self._make_request(user=no_profile_user, branch_id=self.sucursal.id)
        result = self.permission.has_permission(request, self.view)
        self.assertFalse(result)

    def test_rejects_user_without_branch_assignment(self):
        otra_sucursal = Sucursal.objects.create(nombre='Otra Sucursal')
        request = self._make_request(branch_id=otra_sucursal.id)
        result = self.permission.has_permission(request, self.view)
        self.assertFalse(result)

    def test_rejects_inactive_branch(self):
        sucursal_inactiva = Sucursal.objects.create(nombre='Inactiva', activo=False)
        self.user.profile.sucursales.add(sucursal_inactiva)
        request = self._make_request(branch_id=sucursal_inactiva.id)
        result = self.permission.has_permission(request, self.view)
        self.assertFalse(result)
