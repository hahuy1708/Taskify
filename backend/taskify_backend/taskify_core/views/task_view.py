# taskify_core/views/task_view.py

from django.core.exceptions import ValidationError, PermissionDenied
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from taskify_core.serializers import TaskSerializer, TaskDetailSerializer, UpdateTaskSerializer
from taskify_core.models import Task, Team, Project, List
from taskify_auth.models import CustomUser
from taskify_core.permissions import IsLeaderDeleteTask, IsLeaderAssignTaskOrPersonalOwner
from taskify_core.services import create_and_assign_task, list_tasks, update_task, delete_task, get_task_detail
from drf_spectacular.utils import extend_schema
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from taskify_core.middleware import set_current_user

@extend_schema(
    request=TaskSerializer,
    responses=TaskSerializer,
)

@api_view(["POST"])
@permission_classes([IsAuthenticated, IsLeaderAssignTaskOrPersonalOwner])
def create_task(request):
    """
    Leader tạo và gán task cho member.
    Body: {name, description, deadline, priority, project, team, assignee}
    """
    set_current_user(request.user)
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

    if not name or not (project_id or team_id):
        return Response({"detail": "Thiếu thông tin bắt buộc."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        project = Project.objects.get(id=project_id) if project_id else None
        team = Team.objects.get(id=team_id) if team_id else None
        task_list = List.objects.get(id=list_id) if list_id else None

        member = None
        if project and project.is_personal:
            member = leader  # personal: assignee is creator/owner implicitly
        else:
            if not member_id:
                return Response({"detail": "Thiếu assignee cho enterprise project."}, status=status.HTTP_400_BAD_REQUEST)
            member = CustomUser.objects.get(id=member_id)
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
@permission_classes([IsAuthenticated])
def list_tasks_view(request):
    """
    Liệt kê tasks cho admin và user enterprise.
    - Admin xem tất cả tasks.
    - Enterprise user xem tasks trong project/team mình tham gia.
    """
    try:
        tasks = list_tasks(request.user)
        project_id = request.query_params.get('project')
        if project_id:
            try:
                tasks = tasks.filter(project_id=int(project_id))
            except ValueError:
                pass
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@extend_schema(
    responses=TaskDetailSerializer,
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_task_detail_view(request, task_id):
    """Trả về chi tiết đầy đủ của task gồm comments và checklist items."""
    try:
        task = get_task_detail(request.user, task_id)
    except PermissionDenied:
        return Response({"detail": "Bạn không có quyền truy cập task này."}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    serializer = TaskDetailSerializer(task)
    return Response(serializer.data, status=status.HTTP_200_OK)

@extend_schema(
    request=UpdateTaskSerializer,
    responses=TaskSerializer,
)

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_task_view(request, task_id):
    """Cập nhật thông tin task (partial)."""
    set_current_user(request.user)  # Set for signals
    
    update_data = request.data
    serializer = UpdateTaskSerializer(data=update_data, partial=True)
    if not serializer.is_valid():
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    try:
        updated_task = update_task(request.user, task_id, **serializer.validated_data)
    except (ValidationError, PermissionDenied) as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return JsonResponse(TaskSerializer(updated_task).data, status=status.HTTP_200_OK)

@extend_schema(
    summary="Soft delete task",
    description="Set is_deleted=True for the task and related objects.",
    responses={
        204: None,
    },   
)
@api_view(["DELETE"])
@permission_classes([IsLeaderDeleteTask])
def delete_task_view(request, task_id: int):
    """
    Soft delete task by ID.
    - Calls delete_task service.
    - Returns 204 No Content on success.
    """
    try:
        delete_task(user=request.user,task_id=task_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Project.DoesNotExist:
        return Response({"detail": "Project không tồn tại hoặc đã bị xóa."}, status=status.HTTP_404_NOT_FOUND)
    except (ValidationError, PermissionDenied) as e:
        return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
