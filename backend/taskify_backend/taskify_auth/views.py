# taskify_auth/views.py
from rest_framework_simplejwt.views import TokenObtainPairView # type: ignore
from rest_framework.views import APIView # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework import status, permissions # type: ignore
from rest_framework_simplejwt.tokens import RefreshToken # type: ignore
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .serializers import MyTokenObtainPairSerializer, CustomUserCreateSerializer, UserRegistrationResponseSerializer
from .models import CustomUser

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Expect body: {'refresh': '<refresh_token>'}
        This will blacklist the provided refresh token (requires token_blacklist app + migrate)
        """
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'No refresh token provided.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'detail': 'Logout success.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="User Registration",
        description="Custom registration endpoint that saves extra user data",
        request=CustomUserCreateSerializer,
        responses={
            201: UserRegistrationResponseSerializer,
            400: {"description": "Validation error"}
        }
    )
    def post(self, request):
        """
        Custom registration endpoint that saves extra user data
        Expected fields: username, email, password, re_password, full_name, phone_number, birth_date, address
        """
        serializer = CustomUserCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                user = serializer.save()
                return Response({
                    'detail': 'User created successfully',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'full_name': user.full_name,
                        'phone_number': user.phone_number,
                        'birth_date': user.birth_date,
                        'address': user.address,
                        'role': user.role,  # Default: 'user'
                        'is_enterprise': user.is_enterprise,  # Default: False
                        'allow_personal': user.allow_personal  # Default: True
                    }
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'detail': 'Error creating user',
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
