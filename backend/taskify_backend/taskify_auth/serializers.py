# taskify_auth/serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from djoser.serializers import UserSerializer as DjoserUserSerializer
from .models import CustomUser

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user: CustomUser):
        token = super().get_token(user)
        # thêm claims custom
        token['role'] = user.role
        token['full_name'] = user.full_name or user.get_username()
        token['is_enterprise'] = user.is_enterprise
        return token

# Optional: djoser user serializer hiển thị thêm fields
class UserSerializer(DjoserUserSerializer):
    class Meta(DjoserUserSerializer.Meta):
        model = CustomUser
        fields = ('id','username','email','full_name','role','is_enterprise')
