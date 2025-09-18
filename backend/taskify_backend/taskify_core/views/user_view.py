# taskify_core/views/user_views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from taskify_core.serializers import UserSerializer
from taskify_core.services import get_project_leaders, get_team_members


@api_view(["GET"])
@permission_classes([IsAdminUser])
def list_leaders(request, project_id=None):
    leaders = get_project_leaders(project_id)
    serializer = UserSerializer(leaders, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def list_members(request, team_id=None):
    users_qs, membership_map, team_id = get_team_members(team_id)

    if users_qs is None:  # team not found
        return Response({"detail": "Team not found"}, status=404)

    context = {"membership_map": membership_map}
    if team_id:
        context["team_id"] = team_id

    serializer = UserSerializer(users_qs, many=True, context=context)
    return Response(serializer.data)
