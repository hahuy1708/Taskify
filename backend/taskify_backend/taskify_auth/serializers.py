# taskify_auth/serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from djoser.serializers import UserSerializer as DjoserUserSerializer
from djoser.serializers import UserCreateSerializer as DjoserUserCreateSerializer
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from .models import CustomUser

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user: CustomUser):
        token = super().get_token(user)
        token['role'] = user.role
        token['full_name'] = user.full_name or user.get_username()
        token['is_enterprise'] = user.is_enterprise
        return token

class UserSerializer(DjoserUserSerializer):
    class Meta(DjoserUserSerializer.Meta):
        model = CustomUser
        fields = ('id', 'username', 'email', 'full_name', 'role', 'is_enterprise', 'allow_personal', 'phone_number', 'birth_date', 'address')

class UserCreateSerializer(DjoserUserCreateSerializer):
    full_name = serializers.CharField(required=False, allow_blank=True, max_length=255)
    phone_number = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=20)
    birth_date = serializers.DateField(required=False, allow_null=True)
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta(DjoserUserCreateSerializer.Meta):
        model = CustomUser
        fields = (
            'username', 'email', 'password', 're_password',
            'full_name', 'phone_number', 'birth_date', 'address'
        )

class CustomUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)
    re_password = serializers.CharField(style={"input_type": "password"}, write_only=True)
    
    class Meta:
        model = CustomUser
        fields = (
            'username', 'email', 'password', 're_password',
            'full_name', 'phone_number', 'birth_date', 'address'
            # Note: role, is_enterprise, allow_personal are NOT included because they have defaults
            # role defaults to 'user', is_enterprise defaults to False, allow_personal defaults to True
        )
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
            'full_name': {'required': False, 'allow_blank': True},
            'phone_number': {'required': False, 'allow_blank': True, 'allow_null': True},
            'birth_date': {'required': False, 'allow_null': True},
            'address': {'required': False, 'allow_blank': True, 'allow_null': True},
        }

    def validate(self, attrs):
        # Check password match
        if attrs['password'] != attrs['re_password']:
            raise serializers.ValidationError("Passwords don't match.")
        
        # Validate password using Django's password validators
        attrs_copy = attrs.copy()
        attrs_copy.pop('re_password', None)  

        user = CustomUser(**attrs_copy)
        password = attrs.get("password")
        
        try:
            validate_password(password, user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
        
        # Remove re_password from validated data
        attrs.pop('re_password', None)
        return attrs

    def create(self, validated_data):
        try:
            # Use the custom user manager to create user
            user = CustomUser.objects.create_user(**validated_data)
            return user
        except IntegrityError:
            raise serializers.ValidationError("A user with this email or username already exists.")

class UserRegistrationResponseSerializer(serializers.ModelSerializer):
    """Serializer for registration response"""
    class Meta:
        model = CustomUser
        fields = (
            'id', 'username', 'email', 'full_name', 'phone_number', 
            'birth_date', 'address', 'role', 'is_enterprise', 'allow_personal'
        )

    