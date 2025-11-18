# taskify_core/services/team_service.py

from django.core.exceptions import ValidationError, PermissionDenied
from django.shortcuts import get_object_or_404
# from backend.taskify_backend.taskify_core.serializers.team import TeamMembershipSerializer
# from taskify_core.serializers import TeamSerializer
from taskify_core.models import Project, Team, TeamMembership, Task
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

    memberships_created = []
    existing_active = set(team.teammembership_set.filter(is_kicked=False).values_list('user_id', flat=True))
    existing_all = set(team.teammembership_set.values_list('user_id', flat=True))

    new_objs = []
    updated_members = []
    for member_data in members:
        user_id = member_data.get('user_id')
        role = member_data.get('role', '')
        if not user_id:
            raise ValidationError("Mỗi member phải có user_id.")
        member_user = get_object_or_404(CustomUser, id=user_id)
        if not member_user.is_enterprise:
            raise ValidationError(f"User {member_user.username} phải là enterprise user.")
        if user_id in existing_active:
            raise ValidationError(f"User {member_user.username} đã thuộc team này.")
        if user_id in existing_all and user_id not in existing_active:
            # previously kicked - reactivate
            m = TeamMembership.objects.get(user_id=user_id, team=team)
            m.is_kicked = False
            m.role = role
            m.save()
            updated_members.append(m)
        else:
            new_objs.append(TeamMembership(user=member_user, team=team, role=role))

    if new_objs:
        TeamMembership.objects.bulk_create(new_objs)
        memberships_created.extend(new_objs)
    memberships_created.extend(updated_members)
    return memberships_created


def list_teams(user: CustomUser, project_id: int = None):
    if user.role == "admin":
        qs = Team.objects.all()
    elif user.is_enterprise:
        qs = Team.objects.filter(
            Q(leader=user) | Q(teammembership__user=user, teammembership__is_kicked=False) | Q(project__leader=user)
        ).distinct().filter(is_active = True)
    else:
        raise ValidationError("Chỉ admin và enterprise users mới được xem teams.")
    
    if project_id:
        qs = qs.filter(project_id=project_id)
    return qs


def remove_member_from_team(team_id: int, target_user_id: int, request_user: CustomUser, soft: bool = True):
    """
    Remove (kick) a member from a team.
    - Permission: admin, team.leader or project.leader
    - If soft=True set `is_kicked=True` on TeamMembership, otherwise delete the membership row.
    Returns dict with removed flag and soft flag.
    """
    team = get_object_or_404(Team, id=team_id, is_active=True)

    # permission check
    if not (request_user.role == 'admin' or team.leader == request_user or team.project.leader == request_user):
        raise PermissionDenied("Bạn không có quyền loại thành viên này.")

    try:
        target_user = CustomUser.objects.get(id=target_user_id)
    except CustomUser.DoesNotExist:
        raise ValidationError("User không tồn tại.")

    membership_qs = TeamMembership.objects.filter(team=team, user=target_user)
    if not membership_qs.exists():
        raise ValidationError("User không phải là thành viên của team này.")

    if soft:
        membership_qs.update(is_kicked=True)
        # Unassign tasks within the same project that were assigned to this user
        Task.objects.filter(project=team.project, assignee_id=target_user_id, is_deleted=False).update(assignee=None)
    else:
        membership_qs.delete()

    return {"removed": True, "soft": soft}

# def team_detail(user: CustomUser, team_id: int):
#     """
#     Lấy chi tiết 1 team.
#     - Admin có thể xem tất cả team.
#     - Leader của project, leader của team, hoặc thành viên trong team được phép xem.
#     """
#     team = get_object_or_404(
#         Team.objects.prefetch_related(
#             Prefetch('teammembership_set', queryset=TeamMembership.objects.select_related('user'))
#         ).select_related('project', 'leader'),
#         id=team_id,
#         is_active=True
#     )

#     if not (
#         user.role == 'admin' or
#         team.leader == user or
#         team.project.leader == user or
#         team.teammembership_set.filter(user=user).exists()
#     ):
#         raise PermissionDenied("Bạn không có quyền xem chi tiết team này.")

#     return team
