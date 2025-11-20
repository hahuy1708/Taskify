# taskify_core/views/user_views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response
from taskify_auth.models import CustomUser
from taskify_core.serializers import UserSerializer
from taskify_core.services import (
    get_project_leaders,
    get_team_members,
    get_leaders,
    get_all_users_with_membership,
    get_enterprise_leader_candidates,
)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def list_leaders(request, project_id=None):
    search_query = request.query_params.get("search", None)
    if project_id:
        leaders = get_project_leaders(project_id)
    else:
        leaders = get_leaders(search_query)
    
    serializer = UserSerializer(leaders, many=True)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAdminUser])
def list_enterprise_leader_candidates(request):
    """Trả về danh sách enterprise users để chọn làm leader khi tạo enterprise project."""
    search_query = request.query_params.get("search", None)
    candidates = get_enterprise_leader_candidates(search_query)
    serializer = UserSerializer(candidates, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_members(request, team_id=None):
    search_query = request.query_params.get("search", None)
    if team_id:
        users_qs, membership_map, team_id = get_team_members(team_id, search_query)
    else:
        users_qs, membership_map, team_id = get_all_users_with_membership(search_query)
    
    if users_qs is None:  # team not found
        return Response({"detail": "Team not found"}, status=404)

    context = {"membership_map": membership_map}
    if team_id:
        context["team_id"] = team_id

    serializer = UserSerializer(users_qs, many=True, context=context)
    return Response(serializer.data)

