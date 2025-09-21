# taskify_core/services/project_service.py
from django.core.exceptions import ValidationError
from taskify_core.models import Project
from taskify_auth.models import CustomUser

def create_assign_project(admin: CustomUser, name: str, description: str = '', deadline=None,
                   owner: CustomUser = None, leader: CustomUser = None, is_personal: bool = False):
    """
    Service để admin tạo project.
    - admin: request.user (phải là admin)
    - owner, leader: instance CustomUser (hoặc None)
    - deadline: có thể là datetime/str tuỳ client (model sẽ chấp nhận nếu đúng)
    """
    # quyền cơ bản (nếu cần, service vẫn kiểm tra)
    if not admin or admin.role != 'admin':
        raise ValidationError("Chỉ admin mới được tạo project.")

    # owner mặc định là admin
    if owner is None:
        owner = admin

    # Nếu enterprise project (is_personal == False) thì owner phải là admin (theo rule model của bạn)
    if not is_personal and owner.role != 'admin':
        raise ValidationError("Owner phải là admin cho enterprise projects.")

    # leader validation: nếu leader được gán và project là enterprise thì leader phải là enterprise user
    if leader and not leader.is_enterprise and not is_personal:
        raise ValidationError("Leader phải là enterprise user cho enterprise projects.")

    # Tạo đối tượng (model.save() sẽ chạy .clean() và các ràng buộc khác, và tự tạo lists mặc định)
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
