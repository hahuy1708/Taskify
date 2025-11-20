# taskify_core/services/task_service.py

from django.shortcuts import get_object_or_404
from taskify_core.models import Task, Team, Project, List, ChecklistItem, Comment
from taskify_auth.models import CustomUser
from django.core.exceptions import ValidationError
from django.core.exceptions import PermissionDenied
from django.utils import timezone


def create_and_assign_task(leader: CustomUser, member: CustomUser, project: Project, team: Team, name: str, description: str = '', deadline=None, priority=None, task_list: List = None):
    """
    Leader tạo task và gán cho member trong team/project.
    - Chỉ leader của team hoặc project mới được giao task.
    - Member phải thuộc team hoặc project.
    """
    if team and team.project:
        if project and team.project != project:
            raise ValidationError("Team không thuộc project được chỉ định.")
        project = team.project 
    elif not project:
        raise ValidationError("Cần project hoặc team thuộc một project.")

    if project.is_personal:
        if project.owner != leader:
            raise ValidationError("Chỉ owner của personal project mới được tạo task.")
        if team:
            raise ValidationError("Personal project không hỗ trợ teams.")
        member = leader
    else:
        if team:
            if team.leader != leader:
                raise ValidationError("Chỉ leader của team mới được giao task cho thành viên.")
            if not team.teammembership_set.filter(user=member).exists():
                raise ValidationError("Thành viên không thuộc team này.")
        else:
            if project.leader != leader:
                raise ValidationError("Chỉ leader của project mới được giao task cho thành viên.")
            if not Team.objects.filter(project=project, teammembership__user=member).exists():
                raise ValidationError("Thành viên không thuộc project này.")
    

    if task_list:
        if task_list.project != project:
            raise ValidationError("List không thuộc project được chỉ định.")
    else:
        if not project.lists.exists():
            raise ValidationError("Project không có lists. Hãy tạo lists trước.")
        task_list = project.lists.order_by('position').first()  
    
    # Validate task deadline does not exceed project deadline
    if deadline and project.deadline:
        if deadline > project.deadline:
            raise ValidationError(f"Task deadline ({deadline}) không được vượt quá project deadline ({project.deadline.date()}).")
    
    task = Task.objects.create(
        name=name,
        description=description,
        deadline=deadline,
        priority=priority,
        project=project,
        creator=leader,
        assignee=member,
        list=task_list
    )
    return task

def list_tasks(user: CustomUser):
    """
    Liệt kê tasks cho admin và user enterprise.
    - Admin xem tất cả tasks.
    - Leader xem tasks trong project/team mình dẫn dắt.
    - Member xem tasks được giao cho mình trong project/team mình tham gia
    """
    if user.role == 'admin':
        return Task.objects.all()
    elif user.is_enterprise:
        leader_tasks = Task.objects.filter(project__is_personal=False, project__leader=user)
        member_tasks = Task.objects.filter(
            project__is_personal=False,
            assignee=user,
            project__teams__teammembership__user=user
        )
        personal_owner_tasks = Task.objects.filter(project__is_personal=True, project__owner=user)
        personal_assignee_tasks = Task.objects.filter(project__is_personal=True, assignee=user)
        return (leader_tasks | member_tasks | personal_owner_tasks | personal_assignee_tasks).distinct()
    elif user.allow_personal:
        leader_tasks = Task.objects.filter(project__is_personal=True, project__owner=user)
        member_tasks = Task.objects.filter(project__is_personal=True, assignee=user)
        return (leader_tasks | member_tasks).distinct()

    return Task.objects.none()


def _transition_task_status(task: Task, new_list: List, acting_user: CustomUser):
    """Thực hiện chuyển trạng thái task dựa vào list mới.
    Quy tắc thứ tự: To Do (position==1) -> In Progress (==2) -> Done (>=3).
    Chỉ cho phép assignee chuyển trạng thái (leader không can thiệp) theo yêu cầu workflow đơn giản.
    """
    if task.assignee != acting_user:
        raise PermissionDenied("Chỉ assignee mới được thay đổi trạng thái task.")
    if new_list.project != task.project:
        raise ValidationError("List không thuộc cùng project.")

    old_position = task.list.position
    new_position = new_list.position
    if old_position >= 3:
        raise ValidationError("Task đã hoàn thành, không thể thay đổi trạng thái.")
    if new_position < old_position:
        raise ValidationError("Không thể chuyển lùi trạng thái.")
    task.list = new_list

    if new_position == 1:  # To Do
        task.status = 'todo'
        if task.completed_at:
            task.completed_at = None
    elif new_position == 2:  # In Progress
        task.status = 'in_progress'
        if task.completed_at:
            task.completed_at = None
    else:  
        if old_position < 3:
            task.status = 'done'
            task.mark_done(acting_user)  # sets completed_at
        else:
            task.status = 'done'
            if not task.completed_at:
                task.completed_at = timezone.now()
            task.save()
    task.save()
    return task

def update_task(user: CustomUser, task_id: int, **kwargs):
    """Cập nhật metadata hoặc chuyển trạng thái task.
    - Leader: chỉ cập nhật metadata (name, description, deadline, priority, assignee, is_deleted restore).
    - Assignee: chỉ chuyển list -> status (workflow todo -> in_progress -> done).
    """
    task = get_object_or_404(Task, id=task_id)
    project = task.project

    is_leader = (project.leader == user)
    is_assignee = (task.assignee == user)

    if not (is_leader or is_assignee):
        raise PermissionDenied("Chỉ leader hoặc assignee mới được cập nhật task này.")

    # Handle assignee status transition
    if is_assignee and 'list' in kwargs:
        new_list = kwargs.pop('list')
        return _transition_task_status(task, new_list, user)

    # Leader metadata updates
    if is_leader:
        meta_fields = {'name', 'description', 'deadline', 'priority', 'assignee', 'is_deleted'}
        unknown = set(kwargs.keys()) - meta_fields
        if unknown:
            raise ValidationError(f"Leader không thể cập nhật các trường: {', '.join(unknown)}")

        # Restore logic
        if task.is_deleted:
            if 'is_deleted' in kwargs and kwargs['is_deleted'] is False:
                task.is_deleted = False
            else:
                raise PermissionDenied("Task đã bị xóa mềm. Chỉ khôi phục được (is_deleted=False).")

        # Assignee update
        if 'assignee' in kwargs:
            new_assignee = kwargs.pop('assignee')
            if new_assignee is None:
                task.assignee = None
            else:
                if isinstance(new_assignee, CustomUser):
                    assignee_obj = new_assignee
                else:
                    try:
                        assignee_obj = CustomUser.objects.get(id=new_assignee)
                    except CustomUser.DoesNotExist:
                        raise ValidationError("Assignee không tồn tại.")
                if project.is_personal and assignee_obj != task.creator:
                    raise ValidationError("Personal project chỉ gán assignee bằng creator.")
                if not project.is_personal and not Team.objects.filter(project=project, teammembership__user=assignee_obj).exists():
                    raise ValidationError("Assignee không thuộc project này.")
                task.assignee = assignee_obj

        for f in ['name', 'description', 'deadline', 'priority']:
            if f in kwargs:
                # Validate deadline if updating
                if f == 'deadline' and kwargs[f] and project.deadline:
                    if kwargs[f] > project.deadline:
                        raise ValidationError(f"Task deadline ({kwargs[f]}) không được vượt quá project deadline ({project.deadline.date()}).")
                setattr(task, f, kwargs[f])

        if 'is_deleted' in kwargs and kwargs['is_deleted'] is False and task.is_deleted:
            task.is_deleted = False

        task.save()
        return task

    if is_assignee and not kwargs:
        return task

    if is_assignee:
        raise ValidationError("Assignee chỉ được phép thay đổi list để cập nhật trạng thái.")

    return task

def get_task_detail(user: CustomUser, task_id: int):
    """
    Lấy chi tiết task theo id.
    - Leader xem tasks trong project/team mình dẫn dắt.
    - Member xem tasks được giao cho mình trong project/team mình tham gia.
    """
    task = get_object_or_404(Task, id=task_id)

    # Personal projects: allow owner, creator, or assignee regardless of enterprise flag
    if task.project.is_personal:
        if (task.project.owner == user) or (task.creator == user) or (task.assignee == user):
            return task
        raise PermissionDenied("Bạn không có quyền xem task này.")

    # Enterprise projects: allow project leader, or assignee who is a member of the project
    is_leader = (task.project.leader == user)
    is_assignee_member = (task.assignee == user and 
                          Team.objects.filter(project=task.project, teammembership__user=user).exists())
    if is_leader or is_assignee_member:
        return task
    raise PermissionDenied("Bạn không có quyền xem task này.")

def delete_task(user: CustomUser, task_id: int):
    """
    Xử lý soft delete task theo id.
    - Chỉ leader của project, hoặc creator của task mới được xóa.
    """
    task = get_object_or_404(Task, id=task_id, is_deleted=False)

    if user != task.project.leader and user != task.creator:
        raise PermissionDenied("Bạn không có quyền xóa task này.")

    task.is_deleted = True
    task.updated_at = timezone.now()
    task.save(update_fields=["is_deleted", "updated_at"])

    return task 