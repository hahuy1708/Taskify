# taskify_core/views/task_view.py

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from taskify_core.serializers import TaskSerializer
from taskify_core.models import Task, Team, Project, List
from taskify_auth.models import CustomUser
from taskify_core.permissions import IsLeaderAssignTask
from taskify_core.services import create_and_assign_task
from drf_spectacular.utils import extend_schema
from django.db.models import Q

@extend_schema(
    request=TaskSerializer,
    responses=TaskSerializer,
)

@api_view(["POST"])
@permission_classes([IsLeaderAssignTask])
def create_task(request):
    """
    Leader tạo và gán task cho member.
    Body: {name, description, deadline, priority, project, team, assignee}
    """
    data = request.data
    leader = request.user
    member_id = data.get('assignee')
    project_id = data.get('project')
    team_id = data.get('team')
    list_id = data.get('list')
    name = data.get('name')
    description = data.get('description', '')
    deadline = data.get('deadline')
    priority = data.get('priority')

    if not (member_id and name and (project_id or team_id)):
        return Response({"detail": "Thiếu thông tin bắt buộc."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        member = CustomUser.objects.get(id=member_id)
        project = Project.objects.get(id=project_id) if project_id else None
        team = Team.objects.get(id=team_id) if team_id else None
        task_list = List.objects.get(id=list_id) if list_id else None
        task = create_and_assign_task(
            leader=leader,
            member=member,
            project=project,
            team=team,
            name=name,
            description=description,
            deadline=deadline,
            priority=priority,
            task_list=task_list
        )
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    serializer = TaskSerializer(task)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
@api_view(["GET"])
def list_tasks_view(request):
    """
    Liệt kê tasks cho admin và user enterprise.
    - Admin xem tất cả tasks.
    - Enterprise user xem tasks trong project/team mình tham gia.
    """
    user = request.user
    if user.role == 'admin':
        tasks = Task.objects.all()
    elif user.is_enterprise:
        tasks = Task.objects.filter(
            Q(project__leader=user) | 
            Q(project__teams__teammembership__user=user) | 
            Q(assignee=user)
        ).distinct()
    else:
        return Response({"detail": "Chức năng này chỉ dành cho admin và enterprise users mới được xem tasks."}, status=status.HTTP_403_FORBIDDEN)

    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
