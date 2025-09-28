# taskify_core/services/team_service.py

from django.core.exceptions import ValidationError, PermissionDenied
from django.shortcuts import get_object_or_404
from taskify_core.serializers import TeamSerializer
from taskify_core.models import Project, Team, TeamMembership
from taskify_auth.models import CustomUser
from django.db.models import Q, Prefetch

def list_teams(user: CustomUser, project_id: int = None):

    if user.role == "admin":
        qs = Team.objects.all()
    elif user.is_enterprise:
        qs = Team.objects.filter(
            Q(leader=user) | Q(teammembership__user=user) |Q(project__leader=user)
        ).distinct().filter(is_active = True, is_deleted=False)
    else:
        raise ValidationError("Chỉ admin và enterprise users mới được xem teams.")
    
    if project_id:
        qs = qs.filter(project_id=project_id)
    return qs
    