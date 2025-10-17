from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from taskify_core.services import get_admin_stats
from taskify_core.serializers import AdminDashboardStatsSerializer
from django.core.exceptions import PermissionDenied

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard_stats(request):
    """Get admin dashboard statistics"""
    try:
        stats = get_admin_stats(request.user)
        serializer = AdminDashboardStatsSerializer(stats)
        return Response(serializer.data)
    except PermissionDenied as e:
        return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)