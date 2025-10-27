from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from organizacion.models import Usuario


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super(CustomTokenObtainPairSerializer, self).validate(attrs)
        return {
            'access': data['access'],
            'refresh': data['refresh'],
            'username': attrs['username'],
        }
