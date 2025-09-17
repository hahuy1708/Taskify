from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from taskify_core.models import Project, TeamMembership, Team
from taskify_auth.models import CustomUser
from taskify_core.serializers import UserSerializer


@api_view(["GET"])
@permission_classes([IsAdminUser])
def list_leaders(request, project_id=None):
    """
    Lấy danh sách leader của 1 project.
    Nếu không truyền project_id thì trả về tất cả leader của hệ thống.
    """
    if project_id:
        project = get_object_or_404(Project, id=project_id)
        leaders = [project.leader] if project.leader else []
    else:
        leaders = CustomUser.objects.filter(
            id__in=Project.objects.exclude(leader__isnull=True).values_list("leader_id", flat=True)
        ).distinct()

    serializer = UserSerializer(leaders, many=True)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAdminUser])
def list_members(request, team_id=None):
    if team_id:
        # lấy team
        try:
            team = Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            return Response({"detail": "Team not found"}, status=404)

        # lấy memberships của team
        memberships = TeamMembership.objects.filter(team=team).select_related("user")

        # map user_id -> role
        membership_map = {m.user_id: m.role for m in memberships}

        # lấy danh sách user_id từ membership
        user_ids = set(membership_map.keys())

        # thêm leader (nếu chưa nằm trong membership)
        if team.leader_id and team.leader_id not in user_ids:
            user_ids.add(team.leader_id)
            # gán role là "leader"
            membership_map[team.leader_id] = "leader"

        users_qs = CustomUser.objects.filter(id__in=user_ids)
        serializer = UserSerializer(users_qs, many=True, context={
            "team_id": team.id,
            "membership_map": membership_map,
        })
        return Response(serializer.data)

    # không truyền team_id → lấy tất cả user
    users_qs = CustomUser.objects.all()
    memberships = TeamMembership.objects.filter(user_id__in=users_qs).select_related("team")

    membership_map = {}
    for m in memberships:
        membership_map.setdefault(m.user_id, []).append({
            "team_id": m.team_id,
            "team_name": m.team.name if m.team else None,
            "role": m.role,
        })

    teams = Team.objects.select_related("leader")
    for team in teams:
            if team.leader_id:
                membership_map.setdefault(team.leader_id, []).append({
                    "team_id": team.id,
                    "team_name": team.name,
                    "role": "leader",
                })

    serializer = UserSerializer(users_qs, many=True, context={
        "membership_map": membership_map,
    })
    return Response(serializer.data)