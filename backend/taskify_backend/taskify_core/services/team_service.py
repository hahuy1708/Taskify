# taskify_core/services/team_service.py

from django.core.exceptions import ValidationError, PermissionDenied
from django.shortcuts import get_object_or_404
from taskify_core.models import Project, Team, TeamMembership, Task
from taskify_auth.models import CustomUser
from django.db.models import Q, Prefetch
from taskify_core.signals import _log


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
    existing_users = set(team.teammembership_set.values_list('user_id',flat=True))

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
        membership = TeamMembership(user=member_user, team=team, role=role)
        membership.save()  # Use save() instead of bulk_create to trigger signals
        memberships.append(membership)
        existing_users.add(user_id)
    
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

def kick_member_from_team(team_id: int, actor: CustomUser, member_id: int, reassign_to_id: int | None):
    """
    Kick member khỏi team.
    - Chỉ leader của team hoặc project mới được kick.
    - Không thể kick leader của team.
    - Nếu member có tasks chưa hoàn thành (todo/in_progress) trong project của team, bắt buộc chọn reassign_to_id.
    - reassign_to_id phải là member khác trong team và không phải leader.
    - Nếu member không có tasks chưa hoàn thành thì không cần reassign.
    """
    team = get_object_or_404(Team, id=team_id, is_active=True)
    if team.leader != actor and team.project.leader != actor and actor.role != 'admin':
        raise PermissionDenied("Chỉ leader của team hoặc project được kick thành viên.")

    try:
        membership = TeamMembership.objects.get(team=team, user_id=member_id)
    except TeamMembership.DoesNotExist:
        raise ValidationError("Member không thuộc team này.")

    if membership.user == team.leader:
        raise ValidationError("Không thể kick leader của team.")

    reassign_to_user = None
    if reassign_to_id:
        try:
            reassign_to_user = CustomUser.objects.get(id=reassign_to_id)
            if not TeamMembership.objects.filter(team=team, user=reassign_to_user).exists():
                raise ValidationError("Người được gán lại task phải là thành viên trong team.")
        except CustomUser.DoesNotExist:
            raise ValidationError("Người được gán lại task không tồn tại.")

    # Log the kick action before performing it
    _log(
        action_type="member_kicked",
        actor=actor,
        details={
            "team_id": team.id,
            "team_name": team.name,
            "member_id": membership.user.id,
            "member_name": membership.user.username,
            "reassign_to_id": reassign_to_user.id if reassign_to_user else None,
            "reassign_to_name": reassign_to_user.username if reassign_to_user else None,
        }
    )

    # Incomplete tasks in this project assigned to member
    incomplete_qs = Task.objects.filter(
        project=team.project,
        assignee_id=member_id,
        status__in=["todo", "in_progress"],
        is_deleted=False
    )
    incomplete_count = incomplete_qs.count()

    reassigned_count = 0
    reassigned_to_username = None

    if incomplete_count > 0:
        # Must have a reassignment target and it cannot be the leader or the same member
        valid_member_ids = set(
            TeamMembership.objects.filter(team=team)
            .exclude(user_id=member_id)
            .exclude(user=team.leader)
            .values_list("user_id", flat=True)
        )

        if not valid_member_ids:
            # As per requirement, leader cannot take tasks; so if none available -> cannot kick
            raise ValidationError("Không còn member khác (không phải leader) để nhận tasks chưa hoàn thành.")

        if not reassign_to_id:
            raise ValidationError("Member này có tasks chưa hoàn thành. Cần chọn reassign_to_id.")

        if reassign_to_id not in valid_member_ids:
            raise ValidationError("reassign_to_id phải là member khác trong team (không phải leader).")

        reassign_to = CustomUser.objects.get(id=reassign_to_id)
        reassigned_count = incomplete_qs.update(assignee=reassign_to)
        reassigned_to_username = reassign_to.username

        if reassigned_count > 0:
            _log(
                action_type="tasks_reassigned_from_kick",
                actor=actor,
                details={
                    "team_id": team.id,
                    "team_name": team.name,
                    "kicked_member_id": member_id,
                    "kicked_member_name": membership.user.username,
                    "reassign_to_id": reassign_to.id,
                    "reassign_to_name": reassign_to.username,
                    "task_count": reassigned_count,
                }
            )

    # Remove membership
    membership.delete()

    return {
        "kicked_user": membership.user.username,
        "incomplete_tasks_before": incomplete_count,
        "reassigned_tasks": reassigned_count,
        "reassigned_to": reassigned_to_username,
    }
