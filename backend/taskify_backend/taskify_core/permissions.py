# taskify_core/permissions.py
from rest_framework import permissions
from taskify_auth.models import CustomUser
from taskify_core.models import Project, Team, Task

class IsAdminCreateProject(permissions.BasePermission):
    """
    Chỉ admin mới được tạo project và gán leader.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'

class IsLeaderUpdateProjectCompleted(permissions.BasePermission):
    """
    Leader chỉ được cập nhật trường is_completed của project mình làm leader.
    """
    def has_object_permission(self, request, view, obj):
        # obj là Project
        if not isinstance(obj, Project):
            return False
        # Chỉ cho phép PATCH/PUT is_completed
        if request.method in ['PATCH', 'PUT']:
            allowed_fields = set(request.data.keys())
            return obj.leader == request.user and allowed_fields <= {'is_completed'}
        return False

class IsLeaderOfTeam_Project(permissions.BasePermission):
    """
    Chỉ leader của project mới được tạo team cho project đó.
    """
    def has_permission(self, request, view):
        project_id = view.kwargs.get('project_id')
        team_id = view.kwargs.get('team_id')
        if project_id:
            return Project.objects.filter(id=project_id, leader=request.user).exists()
        if team_id:
            return Team.objects.filter(id=team_id, leader=request.user).exists()
        return False

class IsLeaderAssignTask(permissions.BasePermission):
    """
    Chỉ leader của team/project được giao task cho thành viên.
    """
    def has_permission(self, request, view):
        team_id = request.data.get('team')
        project_id = request.data.get('project')
        user = request.user
        if team_id:
            try:
                team = Team.objects.get(id=team_id)
            except Team.DoesNotExist:
                return False
            return team.leader == user
        if project_id:
            try:
                project = Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                return False
            return project.leader == user
        return False
