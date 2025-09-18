# taskify_auth/views.py
from rest_framework_simplejwt.views import TokenObtainPairView # type: ignore
from rest_framework.views import APIView # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework import status, permissions # type: ignore
from rest_framework_simplejwt.tokens import RefreshToken # type: ignore
from .serializers import MyTokenObtainPairSerializer

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
