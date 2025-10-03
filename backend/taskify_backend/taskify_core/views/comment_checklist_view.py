# taskify_core/views/comment_checklist_view.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.core.exceptions import ValidationError, PermissionDenied
from taskify_core.serializers import CommentSerializer, ChecklistItemSerializer
from taskify_core.services.comment_checklist_service import create_comment, delete_comment,list_comment, update_comment
from taskify_core.services.comment_checklist_service import create_checklist_item, delete_checklist_item, list_checklist_item, update_checklist_item
from taskify_core.permissions import IsAllowedForComment, IsAssigneeForCheckList

@extend_schema(
    request=CommentSerializer,
    responses=CommentSerializer
)
@api_view(['POST'])
@permission_classes([IsAllowedForComment])
def create_comment_view(request, task_id):
    try:
        serializer = CommentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        comment = create_comment(request.user, task_id, serializer.validated_data['text'])
        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)
    except (ValidationError, PermissionDenied) as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response({'error': 'Lỗi không xác định'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(
    responses=CommentSerializer(many=True)
)
@api_view(['GET'])
@permission_classes([IsAllowedForComment])
def list_comment_view(request, task_id):
    try:
        comments = list_comment(request.user, task_id,)
        return Response(CommentSerializer(comments, many=True).data)
    except (ValidationError, PermissionDenied) as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response({'error': 'Lỗi không xác định'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(
    request=CommentSerializer,
    responses=CommentSerializer
)
@api_view(['PATCH'])
@permission_classes([IsAllowedForComment])
def update_comment_view(request, comment_id):
    try:
        serializer = CommentSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        comment = update_comment(request.user, comment_id, text=serializer.validated_data.get('text'))
        return Response(CommentSerializer(comment).data)
    except (ValidationError, PermissionDenied) as e:
        return Response ({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response({'error': 'Lỗi không xác định'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(responses={204: None})
@api_view(['DELETE'])
@permission_classes([IsAllowedForComment])
def delete_comment_view(request, comment_id):
    try:
        delete_comment(request.user, comment_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
    except (ValidationError, PermissionDenied) as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response({'error': 'Lỗi không xác định'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# CheckListItem 

@extend_schema(
    request=ChecklistItemSerializer,
    responses=ChecklistItemSerializer
)
@api_view(['POST'])
@permission_classes([IsAssigneeForCheckList])
def create_checklist_item_view(request, task_id):
    try:
        serializer = ChecklistItemSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        item = create_checklist_item(request.user, task_id, serializer.validated_data['name'])
        return Response(ChecklistItemSerializer(item).data, status=status.HTTP_201_CREATED)
    except (ValidationError, PermissionDenied) as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response({'error': 'Lỗi không xác định'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(
    responses=ChecklistItemSerializer(many=True)
)
@api_view(['GET'])
@permission_classes([IsAssigneeForCheckList])
def list_checklist_items_view(request, task_id):
    try:
        items = list_checklist_item(request.user, task_id)
        return Response(ChecklistItemSerializer(items, many=True).data)
    except (ValidationError, PermissionDenied) as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response({'error': 'Lỗi không xác định'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    request=ChecklistItemSerializer,
    responses=ChecklistItemSerializer
)
@api_view(['PATCH'])
@permission_classes([IsAssigneeForCheckList])
def update_checklist_item_view(request, item_id):
    try:
        serializer = ChecklistItemSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        item = update_checklist_item(request.user, item_id, **serializer.validated_data)
        return Response(ChecklistItemSerializer(item).data)
    except (ValidationError, PermissionDenied) as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response({'error': 'Lỗi không xác định'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(responses={204: None})
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_checklist_item_view(request, item_id):
    try:
        delete_checklist_item(request.user, item_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
    except (ValidationError, PermissionDenied) as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response({'error': 'Lỗi không xác định'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)