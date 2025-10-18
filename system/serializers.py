from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super(CustomTokenObtainPairSerializer, self).validate(attrs)
        return {
            'token': data['access'],
            'refresh': data['refresh'],
            'username': attrs['username'],
            'is_admin': User.objects.get(username=attrs['username']).is_manager
        }
