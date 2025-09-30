# taskify_core/views/team_view.py

from django.core.exceptions import ValidationError, PermissionDenied
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import serializers
from taskify_core.serializers import TeamSerializer, TeamMembershipSerializer, TeamCreateSerializer
from taskify_core.models import Task, Team, Project, List
from taskify_auth.models import CustomUser
from taskify_core.services import list_teams, create_team, add_members_to_team
from drf_spectacular.utils import extend_schema, OpenApiExample
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from taskify_core.permissions import IsLeaderCreateTeam
from rest_framework.serializers import ListSerializer


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

@extend_schema(
    request=TeamCreateSerializer,
    responses=TeamSerializer
)

@api_view(["POST"])
@permission_classes([IsLeaderCreateTeam])
def create_team_view(request, project_id):
    """
    Leader của project tạo team cho project đó.
    """
    serializer = TeamCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return Response({"detail": "Project không tồn tại."}, status=status.HTTP_404_NOT_FOUND)

    try:
        team = create_team(
            leader=request.user,
            name=serializer.validated_data["name"],
            project=project
        )
    except (ValidationError, PermissionDenied) as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(TeamSerializer(team).data, status=status.HTTP_201_CREATED)

# @extend_schema(
#     request=ListSerializer(child=serializers.DictField(child=serializers.IntegerField(), example={'user_id': 1, 'role': 'developer'})),
#     responses=TeamMembershipSerializer(many=True),
#     examples=[
#         OpenApiExample(
#             name="Members Input Example",
#             value=[
#                 {"user_id": 5, "role": "developer"},
#                 {"user_id": 6, "role": "tester"}
#             ],
#             description="List of members to add with user_id and optional role."
#         )
#     ]
# )

@extend_schema(
    request=ListSerializer(
        child=serializers.DictField(
            child=serializers.IntegerField()  
        )
    ),
    responses=TeamMembershipSerializer(many=True),
    examples=[
        OpenApiExample(
            name="Members Input Example",
            value=[
                {"user_id": 5, "role": "developer"},
                {"user_id": 6, "role": "tester"}
            ],
            description="List of members to add with user_id and optional role."
        )
    ]
)

@api_view(["POST"])
@permission_classes([IsLeaderCreateTeam])
def add_members_view(request, team_id):
    """
    Thêm thành viên vào team
    """
    members = request.data.get("members", [])
    try:
        memberships = add_members_to_team(request.user, team_id, members)
    except (ValidationError, PermissionDenied) as e:
       return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"added": len(memberships)}, status=status.HTTP_201_CREATED) 
