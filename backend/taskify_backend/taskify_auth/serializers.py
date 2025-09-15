# taskify_auth/serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from djoser.serializers import UserSerializer as DjoserUserSerializer
from djoser.serializers import UserCreateSerializer as DjoserUserCreateSerializer
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


class UserSerializer(DjoserUserSerializer):
    class Meta(DjoserUserSerializer.Meta):
        model = CustomUser
        fields = ('id','username','email','full_name','role','is_enterprise','allow_personal','phone_number','birth_date','address')

class UserCreateSerializer(DjoserUserCreateSerializer):
    class Meta(DjoserUserCreateSerializer.Meta):
        model = CustomUser
        fields = (
            'username',  
            'email',     
            'password',  
            'full_name', 
            'phone_number',
            'birth_date',
            'address',

        )
