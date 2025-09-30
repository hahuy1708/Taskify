# taskify_core/services/project_service.py
from django.core.exceptions import ValidationError, PermissionDenied
from django.shortcuts import get_object_or_404
from taskify_core.serializers import ProjectSerializer
from taskify_core.models import Project, Team, TeamMembership, List, Task
from taskify_auth.models import CustomUser
from django.db.models import Q, Prefetch


def create_assign_project(admin: CustomUser, name: str, description: str = '', deadline=None,
                   owner: CustomUser = None, leader: CustomUser = None, is_personal: bool = False):
    """
    Service để admin tạo project.
    - admin: request.user (phải là admin)
    - owner, leader: instance CustomUser (hoặc None)
    - deadline: có thể là datetime/str tuỳ client (model sẽ chấp nhận nếu đúng)
    """

    if not admin or admin.role != 'admin':
        raise ValidationError("Chỉ admin mới được tạo project.")

    # owner mặc định là admin
    if owner is None:
        owner = admin

    if not is_personal:
        if owner.role != 'admin':
            raise ValidationError("Owner phải là admin cho enterprise projects.")
        if leader and not leader.is_enterprise:
            raise ValidationError("Leader phải là enterprise user cho enterprise projects.")

    project = Project(
        name=name,
        description=description,
        deadline=deadline,
        owner=owner,
        leader=leader,
        is_personal=is_personal
    )

    # gọi save để kích hoạt validation và auto-create lists
    project.save()
    return project

def list_projects(user: CustomUser, include_deleted: bool = False):
    """
    Liệt kê projects cho admin 
    leader chỉ xem được project mình dẫn dắt
    member chỉ xem được project mình tham gia
    """
    if user.role == 'admin':
        qs = Project.objects.all()
    
    elif user.is_enterprise:
        qs = Project.objects.filter(
            Q(leader=user) | Q(teams__teammembership__user=user)
        ).distinct()
    else:
        raise ValidationError("Chỉ admin và enterprise users mới được xem projects.")
    
    if not include_deleted:
        qs = qs.filter(is_deleted=False)
        
    return qs

def user_can_view_project(user: CustomUser, project: Project) -> bool:
    if user.role == 'admin':
        return True
    if project.owner_id == getattr(user, 'id',None):
        return True
    if project.leader_id == getattr(user, 'id',None):
        return True
    return TeamMembership.objects.filter(team__project=project, user=user).exists()

def get_project_kanban(user: CustomUser, project_id: int):
    """
    Lấy project theo định dạng kanban (có nested lists và tasks).
    Chỉ admin, owner, leader, members mới được xem.
    """
    task_qs = Task.objects.filter(is_deleted=False).order_by("created_at").select_related('assignee', 'creator')
    list_qs = List.objects.order_by("position").prefetch_related(Prefetch('tasks', queryset=task_qs))

    project = get_object_or_404(
        Project.objects.prefetch_related(Prefetch('lists', queryset=list_qs)).select_related('owner', 'leader'),
        id=project_id, is_deleted=False
    )
    if project.is_personal and project.owner_id != getattr(user, 'id', None) and user.role != 'admin':
        raise ValidationError("Chỉ có owner hoặc admin mới được xem personal project này.")
    if not user_can_view_project(user, project):
        raise ValidationError("Bạn không có quyền xem project này.")
    return project

def update_project(user: CustomUser, project_id: int, **kwargs):
    """
    Cập nhật project.
    - Admin: được update tất cả field.
    - Leader: chỉ được update description, is_completed.
    """
    project = get_object_or_404(Project, id=project_id, is_deleted=False)

    if user.role == 'admin':
        allowed_fields = {
            'name', 'description', 'deadline', 'owner', 'leader', 'is_personal', 'is_completed'
        }
    elif project.leader == user:
        allowed_fields = {'description', 'is_completed'}
    else:
        raise PermissionDenied("Chỉ admin hoặc leader của project mới được cập nhật.")

    for field, value in kwargs.items():
        if field in allowed_fields:
            setattr(project, field, value)
        else:
            raise ValidationError(f"Không thể cập nhật trường '{field}'.")

    project.save()
    return project

def delete_project(user, project_id: int):
    """
    Xử lý soft delete project theo id.
    - Admin được xóa tất cả project.
    - Leader chỉ được xóa project mà mình làm leader.
    """
    project = get_object_or_404(Project, id=project_id, is_deleted=False)

    if user.role != "admin" and user != project.leader:
        raise ValidationError("Bạn không có quyền xóa project này.")

    project.is_deleted = True
    project.save(update_fields=["is_deleted"])

    return project