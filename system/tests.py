from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase


class SystemTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass")
        self.user_to_test = User.objects.create_user(username="user2", password="pass")
        self.client = APIClient()

    def test_login_endpoint(self):
        url = reverse("token_obtain_pair")
        response = self.client.post(url, {"username": "user", "password": "pass"}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("username", response.data)
        self.assertIn("is_admin", response.data)
        self.assertFalse(response.data["is_admin"])
    
    def test_user_not_found(self):
        url = reverse("token_obtain_pair")
        response = self.client.post(url, {"username": "nonexistent", "password": "pass"}, format='json')
        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.data)
    
    def test_verificar_credenciales(self):
        url = reverse("verificar-admin")
        self.client.login(username="user", password="pass")
        
        # Test with non-staff user
        response = self.client.post(url, {"username": "user2", "password": "pass"}, format='json')
        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.data)
        
        # Make user staff and test again
        self.user_to_test.is_staff = True
        self.user_to_test.save()
        
        response = self.client.post(url, {"username": "user2", "password": "pass"}, format='json')
        self.assertEqual(response.status_code, 200)
