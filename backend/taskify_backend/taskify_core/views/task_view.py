# taskify_core/views/task_view.py

from django.core.exceptions import ValidationError, PermissionDenied
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from taskify_core.serializers import TaskSerializer, UpdateTaskSerializer
from taskify_core.models import Task, Team, Project, List
from taskify_auth.models import CustomUser
from taskify_core.permissions import IsLeaderAssignTask
from taskify_core.services import create_and_assign_task, list_tasks, update_task
from drf_spectacular.utils import extend_schema
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated

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

@extend_schema(
    request=UpdateTaskSerializer,
    responses=TaskSerializer,
)

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_task_view(request, task_id):
    """
    Cập nhật thông tin task.
    """
    try:
        update_data = request.data

        serializer = UpdateTaskSerializer(data=update_data, partial=True)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        updated_task = update_task(request.user, task_id, **serializer.validated_data)
        output_serializer = TaskSerializer(updated_task)
        return JsonResponse(output_serializer.data, status=status.HTTP_200_OK)
    except (ValidationError, PermissionDenied) as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return JsonResponse({'error': 'Lỗi không xác định'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_task_view(request, task_id):
    """
    Xóa (soft delete) task theo id.
    - Chỉ admin, leader của project, hoặc creator của task mới được xóa.
    """
    try:
        task = Task.objects.get(id=task_id, is_deleted=False)
    except Task.DoesNotExist:
        return Response({
            "success": False,
            "message": "Task không tồn tại hoặc đã bị xóa."
        }, status=status.HTTP_404_NOT_FOUND)

    # check quyền
    if (
        request.user.role != "admin"
        and request.user != task.project.leader
        and request.user != task.creator
    ):
        return Response({
            "success": False,
            "message": "Bạn không có quyền xóa task này."
        }, status=status.HTTP_403_FORBIDDEN)

    # soft delete
    task.is_deleted = True
    task.save()

    return Response({
        "success": True,
        "message": "Xóa task thành công."
    }, status=status.HTTP_200_OK)