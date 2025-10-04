# taskify_core/views/user_views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response
from taskify_auth.models import CustomUser

from taskify_core.serializers import UserSerializer
from taskify_core.services import get_project_leaders, get_team_members, lock_user_account


@api_view(["GET"])
@permission_classes([IsAdminUser])
def list_leaders(request, project_id=None):
    leaders = get_project_leaders(project_id)
    serializer = UserSerializer(leaders, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_members(request, team_id=None):
    users_qs, membership_map, team_id = get_team_members(team_id)

    if users_qs is None:  # team not found
        return Response({"detail": "Team not found"}, status=404)

    context = {"membership_map": membership_map}
    if team_id:
        context["team_id"] = team_id

    serializer = UserSerializer(users_qs, many=True, context=context)
    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAdminUser])
def lock_user_view(request, user_id):
    """
    API: Khóa tài khoản người dùng (soft lock)
    Chỉ admin hoặc leader có quyền
    """
    reassign_to = request.data.get("reassign_to")
    reason = request.data.get("reason", "Không có lý do cụ thể")
    try:
        result = lock_user_account(user_id, request.user, reassign_to, reason)
        return Response(result, status=200)
    except CustomUser.DoesNotExist:
        return Response({"detail": "User not found"}, status=404)
    except ValidationError as ve:
        return Response({"detail": str(ve)}, status=400)
    except PermissionDenied as pe:
        return Response({"detail": str(pe)}, status=403)