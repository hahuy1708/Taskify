from rest_framework.permissions import BasePermission, SAFE_METHODS
from taskify_core.models import Team

class IsTeamLeader(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        # obj là Team
        return isinstance(obj, Team) and obj.leader_id == request.user.id
