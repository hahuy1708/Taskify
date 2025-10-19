from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from taskify_core.models import Project, Task
from taskify_auth.models import CustomUser
from django.core.exceptions import PermissionDenied

def calculate_percentage_change(current, previous):
    if previous == 0:
        return 0
    change = ((current - previous) / previous) * 100
    return round(change, 1)

def get_admin_stats(user):
    """Get statistics for admin dashboard"""
    if user.role != 'admin':
        raise PermissionDenied("Only admin can view these stats")

    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    sixty_days_ago = now - timedelta(days=60)

    # Current period stats
    current_projects = Project.objects.filter(is_deleted=False).count()
    current_users = CustomUser.objects.filter(is_active=True).count()
    current_tasks = Task.objects.filter(
        status='done',
        updated_at__gte=thirty_days_ago,
        is_deleted=False
    ).count()

    # Previous period stats
    previous_projects = Project.objects.filter(
        created_at__lt=thirty_days_ago,
        is_deleted=False
    ).count()
    previous_users = CustomUser.objects.filter(
        date_joined__lt=thirty_days_ago,
        is_active=True
    ).count()
    previous_tasks = Task.objects.filter(
        status='done',
        updated_at__gte=sixty_days_ago,
        updated_at__lt=thirty_days_ago,
        is_deleted=False
    ).count()

    # Calculate deltas
    project_delta = calculate_percentage_change(current_projects, previous_projects)
    user_delta = calculate_percentage_change(current_users, previous_users)
    task_delta = calculate_percentage_change(current_tasks, previous_tasks)

    # Calculate productivity
    total_tasks = Task.objects.filter(is_deleted=False).count()
    productivity = round((current_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)
    prev_productivity = round((previous_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)
    productivity_delta = calculate_percentage_change(productivity, prev_productivity)

    return {
        'total_projects': current_projects,
        'active_users': current_users,
        'tasks_completed': current_tasks,
        'productivity': productivity,
        'deltas': {
            'projects': f"+{project_delta}%" if project_delta > 0 else f"{project_delta}%",
            'users': f"+{user_delta}%" if user_delta > 0 else f"{user_delta}%",
            'tasks': f"+{task_delta}%" if task_delta > 0 else f"{task_delta}%",
            'productivity': f"+{productivity_delta}%" if productivity_delta > 0 else f"{productivity_delta}%"
        }
    }

def get_user_stats(user):
    """Get stats for user dashboard"""
    if user.role == 'admin':
        raise PermissionDenied("Admin cannot view user dashboard stats")

    assigned_projects = Project.objects.filter(Q(teams__teammembership__user=user) | Q(leader=user), is_deleted=False).distinct().count()
    assigned_tasks = Task.objects.filter(assignee=user, is_deleted=False).count()
    completed_tasks = Task.objects.filter(assignee=user, status='done', is_deleted=False).count()
    productivity = round((completed_tasks / assigned_tasks * 100) if assigned_tasks > 0 else 0, 1)

    return {
        'assigned_projects': assigned_projects,
        'assigned_tasks': assigned_tasks,
        'completed_tasks': completed_tasks,
        'productivity': productivity
    }
