from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from organizacion.models import Usuario


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super(CustomTokenObtainPairSerializer, self).validate(attrs)
        user = Usuario.objects.get(username=attrs['username'])
        return {
            'access': data['access'],
            'refresh': data['refresh'],
            'username': attrs['username'],
            'email': user.email,
            'avatar': user.avatar.path if user.avatar else None,
        }
