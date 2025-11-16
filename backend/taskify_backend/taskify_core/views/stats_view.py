from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from taskify_core.services import get_admin_stats, get_user_stats, get_tasks_summary, get_tasks_timeseries
from taskify_core.serializers import (
    AdminDashboardStatsSerializer,
    UserDashboardStatsSerializer,
    TaskSummarySerializer,
    TaskTimeseriesPointSerializer,
)
from django.utils.dateparse import parse_date
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
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tasks_summary_view(request):
    if request.user.role != 'admin':
        raise PermissionDenied
    start = request.query_params.get('start')
    end = request.query_params.get('end')
    # parse dates safely (expect YYYY-MM-DD)
    start_date = parse_date(start) if start else None
    end_date = parse_date(end) if end else None
    # validate parsed dates
    if start and not start_date:
        return Response({'detail': 'Invalid start date, expected YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
    if end and not end_date:
        return Response({'detail': 'Invalid end date, expected YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        data = get_tasks_summary(start=start_date, end=end_date)
    except Exception as e:
        return Response({'detail': 'Failed to generate summary', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    serializer = TaskSummarySerializer(data)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tasks_timeseries_view(request):
    if request.user.role != 'admin':
        raise PermissionDenied
    start = request.query_params.get('start')
    end = request.query_params.get('end')
    interval = request.query_params.get('interval', 'day')
    start_date = parse_date(start) if start else None
    end_date = parse_date(end) if end else None
    # validate parsed dates and interval
    if start and not start_date:
        return Response({'detail': 'Invalid start date, expected YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
    if end and not end_date:
        return Response({'detail': 'Invalid end date, expected YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
    if interval not in ('day', 'week'):
        return Response({'detail': "Invalid interval, allowed: 'day' or 'week'"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        data = get_tasks_timeseries(start=start_date, end=end_date, interval=interval)
    except Exception as e:
        return Response({'detail': 'Failed to generate timeseries', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    serializer = TaskTimeseriesPointSerializer(data, many=True)
    return Response(serializer.data)