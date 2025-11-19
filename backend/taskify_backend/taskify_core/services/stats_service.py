from django.db.models import Count, Q, F
from django.utils import timezone
from datetime import timedelta
from taskify_core.models import Project, Task
from taskify_auth.models import CustomUser
from django.core.exceptions import PermissionDenied
from taskify_core.services.project_service import list_projects
from taskify_core.models import Team, TeamMembership

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


def get_reports_overview(user):
    """
    Build admin reports 'Overview' dataset:
    - Project Status Distribution (active/completed/overdue)
    - Task Priority Distribution (open tasks by priority)
    - Project Completion Rate stacked bars (top 10 active projects by total tasks)
    """
    if user.role != 'admin':
        raise PermissionDenied("Only admin can view reports overview")

    now = timezone.now()

    # Project status distribution
    base_projects = Project.objects.filter(is_deleted=False)
    completed = base_projects.filter(is_completed=True).count()
    overdue = base_projects.filter(is_completed=False, deadline__lt=now).count()
    active = base_projects.filter(is_completed=False).exclude(deadline__lt=now).count()

    project_status = {
        'active': active,
        'completed': completed,
        'overdue': overdue,
    }

    # Task priority distribution (OPEN tasks only: todo + in_progress)
    open_tasks = Task.objects.filter(is_deleted=False, status__in=['todo', 'in_progress'])
    task_priority = {
        'high': open_tasks.filter(priority='high').count(),
        'medium': open_tasks.filter(priority='medium').count(),
        'low': open_tasks.filter(Q(priority='low') | Q(priority__isnull=True)).count(),
    }

    # Project completion bars (top 10 active by total tasks)
    proj_qs = (
        base_projects
        .filter(is_completed=False, is_personal=False)
        .annotate(
            total_tasks=Count('tasks', filter=Q(tasks__is_deleted=False), distinct=True),
            done_tasks=Count('tasks', filter=Q(tasks__status='done', tasks__is_deleted=False), distinct=True),
            open_tasks=Count('tasks', filter=Q(tasks__status__in=['todo', 'in_progress'], tasks__is_deleted=False), distinct=True),
        )
        .order_by('-total_tasks')[:10]
    )

    completion_bars = [
        {
            'id': p.id,
            'name': p.name,
            'done': int(getattr(p, 'done_tasks', 0) or 0),
            'remaining': int(getattr(p, 'open_tasks', 0) or 0),
            'total': int(getattr(p, 'total_tasks', 0) or 0),
        }
        for p in proj_qs
    ]

    return {
        'project_status': project_status,
        'task_priority': task_priority,
        'completion_bars': completion_bars,
    }


def get_reports_members_workload(user):
    """
    Build admin reports 'Members Workload' dataset:
    - Team Workload: active tasks per team (todo + in_progress) where assignee is a member of that team and task.project = team.project
    - Top Contributors: top 5 users by completed tasks
    - Projects by Leader: top 5 leaders by number of projects
    """
    if user.role != 'admin':
        raise PermissionDenied("Only admin can view members workload")

    # Team Workload
    teams = (
        Team.objects
        .filter(is_active=True, project__is_deleted=False)
        .select_related('project')
    )

    team_workload = []
    if teams:
        teams = teams.annotate(
            active_tasks=Count(
                'teammembership__user__assigned_tasks',
                filter=Q(
                    teammembership__user__assigned_tasks__is_deleted=False,
                    teammembership__user__assigned_tasks__status__in=['todo', 'in_progress'],
                    teammembership__user__assigned_tasks__project=F('project'),
                ),
                distinct=True,
            )
        ).order_by('-active_tasks')

        for t in teams[:10]:
            team_workload.append({
                'team_id': t.id,
                'team_name': t.name,
                'active_tasks': int(getattr(t, 'active_tasks', 0) or 0),
            })

    # Top Contributors
    top_contributors_qs = (
        CustomUser.objects.filter(is_active=True, is_deleted=False)
        .annotate(
            completed_tasks=Count('assigned_tasks', filter=Q(assigned_tasks__status='done', assigned_tasks__is_deleted=False))
        )
        .order_by('-completed_tasks', 'id')[:5]
    )

    top_contributors = [
      {
        'member_id': u.id,
        'member_name': u.full_name or u.username or u.email,
        'completed_tasks': int(getattr(u, 'completed_tasks', 0) or 0),
      }
      for u in top_contributors_qs
    ]

    # Projects by Leader
    leaders_qs = (
        Project.objects.filter(is_deleted=False, is_personal=False, leader__isnull=False)
        .values('leader', 'leader__full_name', 'leader__username', 'leader__email')
        .annotate(project_count=Count('id'))
        .order_by('-project_count', 'leader')[:5]
    )

    projects_by_leader = [
        {
            'leader_id': row['leader'],
            'leader_name': row['leader__full_name'] or row['leader__username'] or row['leader__email'],
            'project_count': int(row['project_count'] or 0),
        }
        for row in leaders_qs
    ]

    return {
        'team_workload': team_workload,
        'top_contributors': top_contributors,
        'projects_by_leader': projects_by_leader,
    }
