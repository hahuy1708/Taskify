from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from taskify_core.models import Project, TeamMembership
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
    """
    Lấy danh sách member của 1 team.
    Nếu không truyền team_id thì trả về tất cả member thuộc mọi team.
    """
    if team_id:
        memberships = TeamMembership.objects.filter(team_id=team_id)
    else:
        memberships = TeamMembership.objects.all()

    users = CustomUser.objects.filter(id__in=memberships.values_list("user_id", flat=True)).distinct()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)
