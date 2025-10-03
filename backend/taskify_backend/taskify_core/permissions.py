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

class IsLeaderDeleteTask(permissions.BasePermission):
    """
    Chỉ leader của team/project được xoá task
    """
    def has_permission(self, request, view):
        task_id = view.kwargs.get('task_id')
        if not task_id:
            return False
        try:
            task = Task.objects.get(id=task_id, is_deleted=False)
        except Task.DoesNotExist:
            return False
        
        return request.user == task.project.leader or request.user == task.creator

class IsAllowedForComment(permissions.BasePermission):
    """
    Permission cho Comment: Cho phép leader của project/team hoặc member (assignee) của task thao tác (CRUD).
    - Create/List: Check qua task_id từ request (e.g., URL kwargs or data).
    - Retrieve/Update/Delete: Check trên object (Comment).
    """
    def has_permission(self, request, view):
        task_id = request.data.get('task') or view.kwargs.get('task_id')
        if not task_id: return False
        try:
            task = Task.objects.get(id=task_id, is_deleted=False)
        except Task.DoesNotExist:
            return False
        user = request.user
        if user.role == 'admin':
            return True
        team = task.project.teams.filter(leader=user).first() if task.project else None
        return (user == task.project.leader) or (team and user == team.leader) or (user == task.assignee)
    def has_object_permission(self, request, view, obj):
        task = obj.task
        if task.is_deleted:
            return False
        user = request.user
        if user.role == 'admin':
            return True
        team = task.project.teams.filter(leader=user).first() if task.project else None
        return (user == task.project.leader) or (team and user == team.leader) or (user == task.assignee) or (user == obj.user)
    
class IsAssigneeForCheckList(permissions.BasePermission):
    def has_permission(self, request, view):
        task_id = request.data.get('task') or view.kwargs.get('task_id')
        if not task_id:
            return False
        try:
            task = Task.objects.get(id=task_id, is_deleted=False)
        except Task.DoesNotExist:
            return False
        user = request.user
        return user == task.assignee
    def has_object_permission(self, request, view, obj):
        task = obj.task
        if task.is_deleted:
            return False
        user = request.user
        return user == task.assignee
        
