# taskify_core/services/team_service.py

from django.core.exceptions import ValidationError, PermissionDenied
from django.shortcuts import get_object_or_404
from taskify_core.serializers import TeamSerializer
from taskify_core.models import Project, Team, TeamMembership
from taskify_auth.models import CustomUser
from django.db.models import Q, Prefetch


def create_team(leader: CustomUser,name: str, project: Project):
    """
    Leader của project tạo team cho project đó.
    - Chỉ leader của project mới được tạo team.
    """
    if project.leader != leader:
        raise ValidationError("Chỉ leader của project mới được tạo team.")
    if project.is_personal:
        raise ValidationError("Team chỉ cho enterprise project")
    team = Team.objects.create(
        name=name,
        project=project,
        leader=leader
    )
    return team

def add_members_to_team(team_id: int, user: CustomUser,members: list):
    """
    Thêm nhiều thành viên vào team (bulk add).
    - Chỉ leader của team hoặc project mới được thêm members.
    - Members: list of dicts [{'user_id': int, 'role': str (optional)}]
    - Users phải enterprise
    """
    team = get_object_or_404(Team, id=team_id, is_active=True)
    if team.leader != user and team.project.leader != user:
        raise ValidationError("Chỉ leader của team hoặc project được thêm thành viên")

    memberships = []
    existing_users = set(team.teammembership_set.values_list('user_id'),flat=True)

    for member_data in members:
        user_id = member_data.get('user_id')
        role = member_data.get('role', '')
        if not user_id:
            raise ValidationError("Mỗi member phải có user_id.")
        member_user = get_object_or_404(CustomUser, id=user_id)
        if not member_user.is_enterprise:
            raise ValidationError(f"User {member_user.username} phải là enterprise user.")
        if user_id in existing_users:
            raise ValidationError(f"User {member_user.username} đã thuộc team này.")
        memberships.append(TeamMembership)(user=member_user, team=team,role=role)
        existing_users.add(user_id)
    
    TeamMembership.objects.bulk_create(memberships)
    return memberships


def list_teams(user: CustomUser, project_id: int = None):

    if user.role == "admin":
        qs = Team.objects.all()
    elif user.is_enterprise:
        qs = Team.objects.filter(
            Q(leader=user) | Q(teammembership__user=user) |Q(project__leader=user)
        ).distinct().filter(is_active = True)
    else:
        raise ValidationError("Chỉ admin và enterprise users mới được xem teams.")
    
    if project_id:
        qs = qs.filter(project_id=project_id)
    return qs
    