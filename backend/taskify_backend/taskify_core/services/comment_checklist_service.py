# taskify_core/services/comment_checklist_service.py

from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError, PermissionDenied
from taskify_core.models import Comment, ChecklistItem, Task
from taskify_auth.models import CustomUser
from django.utils import timezone

def create_comment(user: CustomUser, task_id: int, text: str):
    task = get_object_or_404(Task, id=task_id, is_deleted=False)
    if user != task.assignee and user != task.project.leader and user != task.creator:
        raise PermissionDenied("Chỉ participant của task mới comment.")
    if not text.strip():
        raise ValidationError("Text không rỗng.")
    return Comment.objects.create(user=user, task=task, text=text)

def list_comment(user: CustomUser, task_id: int):
    task = get_object_or_404(Task, id=task_id, is_deleted=False)
    if user != task.assignee and user != task.project.leader and user != task.creator:
        raise PermissionDenied("Chỉ participant của task mới xem được comment.")
    comments = Comment.objects.filter(task_id=task_id, is_deleted=False).order_by("created_at")
    return comments

def update_comment(user: CustomUser, comment_id: int, new_text: str):
    comment = get_object_or_404(Comment,id=comment_id,is_deleted=False)
    if comment.user != user:
        raise PermissionDenied("Bạn không có quyên chỉnh sửa comment này")
    
    if not new_text.strip():
        raise ValidationError("Comment không được để trống.")
    
    comment.text = new_text.strip()
    comment.updated_at = timezone.now()
    comment.save(update_fields=["text", "updated_at"])
    
    return comment

def delete_comment(user: CustomUser, comment_id: int):
    comment = get_object_or_404(Comment, id=comment_id, is_deleted=False)
    if user.role != 'admin' and user != comment.user and user != comment.task.project.leader and user != comment.task.assignee:
        raise PermissionDenied("Chỉ owner, leader hoặc admin xóa comment.")
    comment.delete()  # Hard delete

def create_checklist_item(user: CustomUser, task_id: int, name: str):
    task = get_object_or_404(Task, id=task_id, is_deleted=False)
    if user != task.assignee:
        raise PermissionDenied("Chỉ assignee tạo checklist item.")
    if not name.strip():
        raise ValidationError("Name không rỗng.")
    return ChecklistItem.objects.create(task=task, name=name)

def list_checklist_item(user: CustomUser, task_id: int):
    task = get_object_or_404(Task, id=task_id,is_deleted=False)
    if user != task.assignee:
        raise PermissionDenied("Chỉ member được giao task mới xem được checklist.")
    items = ChecklistItem.objects.filter(task_id=task_id,is_deleted=False).order_by("created_at")
    return items

def update_checklist_item(user: CustomUser,item_id: int, new_name: str):
    item = get_object_or_404(ChecklistItem, id=item_id,is_deleted=False)
    if user != item.task.assignee:
        raise PermissionDenied("Chỉ assignee được update checklist item.")
    if not new_name.strip():
        raise ValidationError("Name không rỗng")
    item.name = new_name
    item.save(update_fields=["name"])
    return item

def delete_checklist_item(user: CustomUser, item_id: int):
    item = get_object_or_404(ChecklistItem, id=item_id, is_deleted=False)
    if user != item.task.assignee:
        raise PermissionDenied("Chỉ assignee xóa checklist item.")
    item.delete()  # Hard delete

# Cascade soft khi delete Task (ở task_service.delete_task)
# def soft_delete_task_children(task: Task):
#     task.comments.update(is_deleted=True)
#     task.checklist_items.update(is_deleted=True)