# taskify_core/services/task_service.py

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
        # Kiểm tra member có trong team
        if not team.teammembership_set.filter(user=member).exists():
            raise ValidationError("Thành viên không thuộc team này.")
    elif project:
        if project.leader != leader:
            raise ValidationError("Chỉ leader của project mới được giao task cho thành viên.")
        # Kiểm tra member có trong project (thông qua team)
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
        task_list = project.lists.order_by('position').first()  # Hoặc .order_by('position').first() để lấy 'To Do'
    
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