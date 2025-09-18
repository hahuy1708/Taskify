# taskify_core/services/user_service.py
from django.shortcuts import get_object_or_404
from taskify_core.models import Project, TeamMembership, Team
from taskify_auth.models import CustomUser

def get_project_leaders(project_id=None):
    """Trả về queryset leaders theo project_id hoặc toàn hệ thống."""
    if project_id:
        project = get_object_or_404(Project, id=project_id)
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
