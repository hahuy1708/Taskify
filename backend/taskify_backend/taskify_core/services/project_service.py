# taskify_core/services/project_service.py
from django.core.exceptions import ValidationError
from taskify_core.serializers import ProjectSerializer
from taskify_core.models import Project
from taskify_auth.models import CustomUser
from django.db.models import Q


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

