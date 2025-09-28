# taskify_core/views/team_view.py

from django.core.exceptions import ValidationError, PermissionDenied
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from taskify_core.serializers import TeamSerializer
from taskify_core.models import Task, Team, Project, List
from taskify_auth.models import CustomUser
from taskify_core.services import list_teams
from drf_spectacular.utils import extend_schema
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated


@extend_schema(
    responses=TeamSerializer(many=True)
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_team_view(request):
    """
    Liệt kê teams cho admin và user enterprise.
    - Admin xem tất cả teams.
    - Enterprise user xem teams trong project mình tham gia.
    """
    project_id = request.query_params.get("project_id")
    teams = list_teams(request.user)
    return Response(TeamSerializer(teams,many=True).data)   


