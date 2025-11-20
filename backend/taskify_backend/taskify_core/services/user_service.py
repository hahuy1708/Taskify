# taskify_core/services/user_service.py
from django.shortcuts import get_object_or_404
from taskify_core.models import Project, TeamMembership, Team, Task
from taskify_auth.models import CustomUser
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.utils import timezone
from django.db.models import Q
from typing import Optional

def _filter_by_search(qs, search_query: Optional[str]):
    """Áp dụng bộ lọc tìm kiếm (username/email/full_name) nếu có."""
    if not search_query:
        return qs
    return qs.filter(
        Q(username__icontains=search_query)
        | Q(email__icontains=search_query)
        | Q(full_name__icontains=search_query)
    )

def get_project_leaders(project_id=None):
    """Trả về queryset leaders theo project_id"""
    if project_id:
        project = get_object_or_404(Project, id=project_id, is_deleted=False)
        return [project.leader] if project.leader else []

def get_leaders(search_query=None):
    """Trả về queryset tất cả leaders trong hệ thống."""
    leader_qs = CustomUser.objects.filter(
        id__in=Project.objects.exclude(leader__isnull=True).values_list("leader_id", flat=True)
    ).distinct()
    leader_qs = _filter_by_search(leader_qs, search_query)
    
    return leader_qs

def get_enterprise_leader_candidates(search_query=None):
    """Danh sách enterprise users (có thể được chọn làm leader khi tạo enterprise project)."""
    qs = CustomUser.objects.filter(is_enterprise=True)
    qs = _filter_by_search(qs, search_query)
    return qs


def get_all_users_with_membership(search_query=None):
    users_qs = CustomUser.objects.all()
    users_qs = _filter_by_search(users_qs, search_query)
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

def get_team_members(team_id=None, search_query= None):
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
        users_qs = _filter_by_search(users_qs, search_query)
        return users_qs, membership_map, team_id


