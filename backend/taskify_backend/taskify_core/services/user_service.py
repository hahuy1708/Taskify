# taskify_core/services/user_service.py
from django.shortcuts import get_object_or_404
from taskify_core.models import Project, TeamMembership, Team, Task, UserLockHistory
from taskify_auth.models import CustomUser
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.utils import timezone

def get_project_leaders(project_id=None):
    """Trả về queryset leaders theo project_id hoặc toàn hệ thống."""
    if project_id:
        project = get_object_or_404(Project, id=project_id, is_deleted=False)
        return [project.leader] if project.leader else []
    return CustomUser.objects.filter(
        id__in=Project.objects.exclude(leader__isnull=True).values_list("leader_id", flat=True)
    ).distinct()


def get_team_members(team_id=None):
    """Trả về tuple (users_qs, membership_map, team_id)."""
    if team_id:
        try:
            team = Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            return None, None, None

        memberships = TeamMembership.objects.filter(team=team).select_related("user")
        membership_map = {m.user_id: m.role for m in memberships}
        user_ids = set(membership_map.keys())

        # thêm leader nếu chưa có
        if team.leader_id and team.leader_id not in user_ids:
            user_ids.add(team.leader_id)
            membership_map[team.leader_id] = "leader"

        users_qs = CustomUser.objects.filter(id__in=user_ids)
        return users_qs, membership_map, team.id

    # không có team_id → trả toàn bộ user + membership_map
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

    return users_qs, membership_map, None

def lock_user_account(user_id, request_user, reassign_to=None, reason=None):
    """
    Khóa tài khoản người dùng.
    Chỉ admin hoặc leader của project có quyền thực hiện.
    """
    # Lấy user cần khóa
    try:
        user = CustomUser.objects.get(id=user_id, is_deleted=False)
    except CustomUser.DoesNotExist:
        raise ValidationError("User không tồn tại.")
    
    if not user.is_active:
        raise ValidationError("Tài khoản đã bị khóa trước đó.")
    
    # Kiểm tra quyền
    if request_user.role != 'admin':
        # Tìm project mà cả 2 cùng tham gia
        same_projects = Project.objects.filter(members=user, leader=request_user)
        # Hoặc kiểm tra trong bảng TeamMembership nếu có
        is_leader = TeamMembership.objects.filter(
            user=request_user,
            role='leader',
            is_active=True,
            project__in=same_projects
        ).exists()
        if not is_leader:
            raise PermissionDenied("Bạn không có quyền khóa tài khoản này.")
    
    # Khóa tài khoản
    user.is_active = False
    user.locked_at = timezone.now()
    user.save()

    # Ghi log
    UserLockHistory.objects.create(
        user=user,
        locked_by=request_user,
        reason=reason 
    )


    # Gỡ user khỏi các team
    TeamMembership.objects.filter(user=user).update(is_active=False)

    # Chuyển giao hoặc gỡ bỏ task
    tasks = Task.objects.filter(assignee=user)
    if reassign_to:
        try:
            new_assignee = CustomUser.objects.get(id=reassign_to, is_deleted=False)
        except CustomUser.DoesNotExist:
            raise ValidationError("Người nhận nhiệm vụ mới không tồn tại.")
        reassigned_count = tasks.update(assignee=new_assignee)
    else:
        reassigned_count = tasks.update(assignee=None)

    return {
        "message": f"Tài khoản {user.username} đã bị khóa.",
        "reassigned_tasks": reassigned_count,
    }