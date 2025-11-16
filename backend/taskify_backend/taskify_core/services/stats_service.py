from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from taskify_core.models import Project, Task
from taskify_auth.models import CustomUser
from django.core.exceptions import PermissionDenied
from taskify_core.services.project_service import list_projects

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

    current_projects = Project.objects.filter(is_deleted=False).count()
    current_users = CustomUser.objects.filter(is_active=True).count()
    current_tasks = Task.objects.filter(
        status='done',
        updated_at__gte=thirty_days_ago,
        is_deleted=False
    ).count()

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
    urgent_issues = []
    try:
        now_dt = timezone.now()
        now_date = now_dt.date()
        upcoming_date = (now_dt + timedelta(days=7)).date()

        qs = list_projects(user, include_deleted=False)
        # exclude already completed projects
        qs = qs.filter(is_completed=False)

        # include projects due within next 7 days OR recently overdue (e.g., last 30 days)
        overdue_window_days = 30
        overdue_cutoff = (now_dt - timedelta(days=overdue_window_days)).date()

        date_filter = Q(deadline__date__gte=now_date, deadline__date__lte=upcoming_date) | Q(deadline__date__lt=now_date, deadline__date__gte=overdue_cutoff)
        # use deadline__date lookup so DateTimeField timezone differences don't exclude items
        qs = qs.filter(deadline__isnull=False).filter(date_filter).order_by('deadline')[:10]

        for p in qs:
            prog = getattr(p, 'progress', 0.0) or 0.0
            try:
                prog = float(prog)
            except Exception:
                prog = 0.0
            if prog < 50.0:
                leader = None
                if getattr(p, 'leader', None):
                    leader = {'id': p.leader.id, 'username': p.leader.username}

                due_in_days = None
                if p.deadline:
                    try:
                        due_in_days = (p.deadline.date() - now.date()).days
                        if due_in_days < 0:
                            due_in_days = f"{abs(due_in_days)}d overdue"
                    except Exception:
                        due_in_days = None

                urgent_issues.append({
                    'project_id': p.id,
                    'project_name': p.name,
                    'deadline': p.deadline.isoformat() if p.deadline else None,
                    'progress': round(prog, 1),
                    'leader': leader,
                    'due_in_days': due_in_days,
                })
    except Exception:
        # be defensive: if project_service isn't available or query fails, return empty list
        urgent_issues = []

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
        },
        'urgent_issues': urgent_issues
    }

def get_user_stats(user):
    """Get stats for user dashboard"""
    if user.role == 'admin':
        raise PermissionDenied("Admin cannot view user dashboard stats")

    assigned_projects = Project.objects.filter(Q(teams__teammembership__user=user) | Q(leader=user), is_deleted=False).distinct().count()
    assigned_tasks = Task.objects.filter(assignee=user, is_deleted=False).count()
    completed_tasks = Task.objects.filter(assignee=user, status='done', is_deleted=False).count()
    productivity = round((completed_tasks / assigned_tasks * 100) if assigned_tasks > 0 else 0, 1)

    now = timezone.now().date()
    upcoming = now + timedelta(days=7)

    upcoming_deadlines = []

    upcoming_qs = Task.objects.filter(
        assignee=user,
        is_deleted=False,
        deadline__isnull=False,
        deadline__gte=now,
        deadline__lte=upcoming
    ).select_related('project').order_by('deadline')[:10]

    # serialize queryset to simple dicts so views/serializers can return JSON easily
    for t in upcoming_qs:
        upcoming_deadlines.append({
            'id': t.id,
            'name': t.name,
            'deadline': t.deadline.isoformat() if t.deadline else None,
            'project': {'id': t.project.id, 'name': t.project.name} if t.project else None,
            'assignee': {'id': t.assignee.id, 'username': t.assignee.username} if t.assignee else None,
            'status': t.status,
            'due_in_days': (t.deadline - now).days if t.deadline else None,
        })

    return {
        'assigned_projects': assigned_projects,
        'assigned_tasks': assigned_tasks,
        'completed_tasks': completed_tasks,
        'productivity': productivity,
        'upcoming_deadlines': upcoming_deadlines
    }
