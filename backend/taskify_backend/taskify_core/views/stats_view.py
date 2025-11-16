from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from taskify_core.services import get_admin_stats, get_user_stats
from taskify_core.serializers import AdminDashboardStatsSerializer, UserDashboardStatsSerializer
from django.core.exceptions import PermissionDenied

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dashboard_stats(request):
    """API endpoint to get dashboard statistics for admin or user."""
    user = request.user
    try:
        if user.role == 'admin':
            stats = get_admin_stats(user)
            serializer = AdminDashboardStatsSerializer(stats)
        else:
            stats = get_user_stats(user)
            serializer = UserDashboardStatsSerializer(stats)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except PermissionDenied as e:
        return Response({'detail': str(e)}, status=status.HTTP_403_FORBIDDEN)
