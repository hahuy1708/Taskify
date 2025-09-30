# taskify_core/services/task_service.py

from django.shortcuts import get_object_or_404
from taskify_core.models import Task, Team, Project, List
from taskify_auth.models import CustomUser
from django.core.exceptions import ValidationError

def create_and_assign_task(leader: CustomUser, member: CustomUser, project: Project, team: Team, name: str, description: str = '', deadline=None, priority=None, task_list: List = None):
    """
    Leader tạo task và gán cho member trong team/project.
    - Chỉ leader của team hoặc project mới được giao task.
    - Member phải thuộc team hoặc project.
    """
    # Infer project từ team nếu không có project param
    if team and team.project:
        if project and team.project != project:
            raise ValidationError("Team không thuộc project được chỉ định.")
        project = team.project  # Sử dụng project của team
    elif not project:
        raise ValidationError("Cần project hoặc team thuộc một project.")

    # Kiểm tra leader có quyền giao task
    if team:
        if team.leader != leader:
            raise ValidationError("Chỉ leader của team mới được giao task cho thành viên.")
        
        if not team.teammembership_set.filter(user=member).exists():
            raise ValidationError("Thành viên không thuộc team này.")
    elif project:
        if project.leader != leader:
            raise ValidationError("Chỉ leader của project mới được giao task cho thành viên.")

        if not Team.objects.filter(project=project, teammembership__user=member).exists():
            raise ValidationError("Thành viên không thuộc project này.")
    else:
        raise ValidationError("Thiếu thông tin team hoặc project.")

    if task_list:
        if task_list.project != project:
            raise ValidationError("List không thuộc project được chỉ định.")
    else:
        if not project.lists.exists():
            raise ValidationError("Project không có lists. Hãy tạo lists trước.")
        task_list = project.lists.order_by('position').first()  
    
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
    - Member xem tasks được giao cho mình trong project/team mình tham gia.
    """
    if user.role == 'admin':
        return Task.objects.all()
    
    elif user.is_enterprise:
        leader_tasks = Task.objects.filter(
            project__leader=user
        )
        member_tasks = Task.objects.filter(
            assignee=user,
            project__teams__teammembership__user=user
        )
        return (leader_tasks | member_tasks).distinct()
    
    else:
        raise ValidationError("Chức năng này chỉ dành cho admin và enterprise users.")
    
def update_task(user: CustomUser, task_id: int, **kwargs):
    """
    Cập nhật task.
    - Chỉ leader của project/team mới được cập nhật metadata của task.
    - Member chỉ được cập nhật trạng thái của task được giao.
    """
    task = get_object_or_404(Task, id=task_id, is_deleted=False)
    project = task.list.project # Task -> List -> Project

    is_leader = (project.leader == user)
    is_assignee = (task.assignee == user)

    if not (is_leader or is_assignee):
        raise ValidationError("Chỉ leader hoặc assignee mới được cập nhật task này.")

    if is_leader:
        allowed_fields = {'name', 'description', 'deadline', 'priority', 'assignee'}
        if 'assignee' in kwargs:
            new_assignee = kwargs.pop('assignee')
            if new_assignee is not None:
                try:
                    new_assignee = CustomUser.objects.get(id=new_assignee)
                except CustomUser.DoesNotExist:
                    raise ValidationError("Assignee không tồn tại.")
                if not Team.objects.filter(project=project, teammembership__user=new_assignee).exists():
                    raise ValidationError("Assignee không thuộc project này.")
                task.assignee = new_assignee
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(task, field, value)
            else: 
                raise ValidationError(f"Không thể cập nhật trường '{field}'.")
        
    elif is_assignee:
        allowed_fields = {'list'}
        if set(kwargs.keys()) - allowed_fields:
            raise ValidationError("Member chỉ được cập nhật trạng thái của task.")
        if 'list' in kwargs:
            new_list = kwargs['list']
            if new_list.project != project:
                raise ValidationError("List không thuộc project này.")
            old_position = task.list.position
            task.list = new_list
            new_position = new_list.position
            if new_position == 1:
                task.status = 'to do'
                if task.completed_at:
                    task.completed_at = None
            elif new_position == 2:
                task.status = 'in progress'
                if task.completed_at:
                    task.completed_at = None
            else:
                task.status = 'done'
                if old_position < 3: # <3 is not done before
                    task.mark_done(user)
                else:
                    task.saved() 
    task.save()
    return task

