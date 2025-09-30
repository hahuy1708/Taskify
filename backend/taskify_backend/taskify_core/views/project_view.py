# taskify_core/views/project_view.py
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.core.exceptions import ValidationError, PermissionDenied
from rest_framework.permissions import IsAuthenticated

from taskify_core.models import Project
from taskify_core.serializers import ProjectSerializer, ProjectKanbanSerializer, UpdateProjectSerializer
from taskify_core.permissions import IsAdminCreateProject
from taskify_auth.models import CustomUser
from taskify_core.services import create_assign_project, list_projects, user_can_view_project, get_project_kanban, update_project, delete_project

@extend_schema(
    request=ProjectSerializer,
    responses=ProjectSerializer,
)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_projects_view(request):
    """
    Liệt kê projects cho admin
    """
    user = request.user
    include_deleted = request.query_params.get('include_deleted', 'false').lower() in ('true', '1', 'yes')

    try:
        projects = list_projects(user=user, include_deleted=include_deleted)
    except ValidationError as ve:
        msg = ve.message_dict if hasattr(ve, "message_dict") else ve.messages if hasattr(ve, "messages") else str(ve)
        return Response({"detail": msg}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    serializer = ProjectSerializer(projects, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def retrieve_project_view(request, project_id: int):
    """
    GET/projects/{project_id}/kanba - Project -> lists -> tasks
    """
    try:
        project = get_project_kanban(request.user, project_id)
    except ValidationError as e:
        return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProjectKanbanSerializer(project)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAdminCreateProject])
def create_project(request):
    """
    Admin tạo project (view chỉ parse input và gọi project_service.create_project).
    Body: { name, description?, deadline?, owner?, leader?, is_personal? }
    """
    data = request.data
    name = data.get("name")
    if not name:
        return Response({"detail": "Thiếu trường 'name'."}, status=status.HTTP_400_BAD_REQUEST)

    # Lấy owner (nếu gửi id)
    owner = None
    owner_id = data.get("owner")
    if owner_id:
        try:
            owner = CustomUser.objects.get(id=owner_id)
        except CustomUser.DoesNotExist:
            return Response({"detail": "Owner không tồn tại."}, status=status.HTTP_400_BAD_REQUEST)

    # Lấy leader (nếu gửi id)
    leader = None
    leader_id = data.get("leader")
    if leader_id:
        try:
            leader = CustomUser.objects.get(id=leader_id)
        except CustomUser.DoesNotExist:
            return Response({"detail": "Leader không tồn tại."}, status=status.HTTP_400_BAD_REQUEST)

    description = data.get("description", "")
    deadline = data.get("deadline", None)
    is_personal = data.get("is_personal", False)
    if isinstance(is_personal, str):
        is_personal = is_personal.lower() in ("true", "1", "yes")

    try:
        project = create_assign_project(
            admin=request.user,
            name=name,
            description=description,
            deadline=deadline,
            owner=owner,
            leader=leader,
            is_personal=is_personal
        )
    except ValidationError as ve:
        # chuẩn hoá message trả về
        msg = ve.message_dict if hasattr(ve, "message_dict") else ve.messages if hasattr(ve, "messages") else str(ve)
        return Response({"detail": msg}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    serializer = ProjectSerializer(project)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@extend_schema(
    request=UpdateProjectSerializer,
    responses=ProjectSerializer,
)

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_project_view(request, project_id: int):
    """
    Cập nhật project:
    - Admin: update được tất cả field.
    - Leader: chỉ update description, is_completed.
    Luôn dùng PATCH.
    """
    try:
        serializer = UpdateProjectSerializer(
            data=request.data,
            partial=True,
            context={'request': request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        updated_project = update_project(
            user=request.user,
            project_id=project_id,
            **serializer.validated_data
        )
        output_serializer = ProjectSerializer(updated_project)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    except (ValidationError, PermissionDenied) as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except Exception:
        return JsonResponse({'error': 'Lỗi không xác định'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_project_view(request, project_id: int):
    try:
        project = delete_project(request.user, project_id)
        return Response({
            "success": True,
            "message": f"Xóa project '{project.name}' thành công."
        }, status=status.HTTP_200_OK)
    except ValidationError as e:
        return Response({
            "success": False,
            "message": str(e)
        }, status=status.HTTP_403_FORBIDDEN)
    except Exception:
        return Response({
            "success": False,
            "message": "Project không tồn tại hoặc đã bị xóa."
        }, status=status.HTTP_404_NOT_FOUND)