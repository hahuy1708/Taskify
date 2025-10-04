# backend/taskify_backend/taskify_core/models.py
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from taskify_auth.models import CustomUser, Notification

class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='owned_projects')  # Admin tạo, là owner ban đầu
    leader = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.SET_NULL, related_name='leading_projects')  # Admin gán leader
    is_personal = models.BooleanField(default=False)  # True cho personal
    is_completed = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)  # Soft delete
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=['is_personal', 'is_completed'])]

    def clean(self):
        if self.is_personal and not self.owner.allow_personal:
            raise ValidationError("Owner không được phép tạo personal projects.")

    def save(self, *args, **kwargs):
        if not self.is_personal:
            if self.owner.role != 'admin':  # Chỉ admin tạo enterprise
                raise ValidationError("Chỉ admin tạo enterprise projects.")
            if self.leader and not self.leader.is_enterprise:
                raise ValidationError("Leader phải là enterprise user.")
        super().save(*args, **kwargs)
        if not self.lists.exists():  # Auto tạo default lists khi save
            List.objects.bulk_create([
                List(name='To Do', position=1, project=self),
                List(name='In Progress', position=2, project=self),
                List(name='Done', position=3, project=self),
            ])

    def __str__(self):
        kind = "Personal" if self.is_personal else "Enterprise"
        return f"{self.name} [{kind}]"

class List(models.Model):  # Kanban columns, đơn giản hóa: Chỉ name/position
    name = models.CharField(max_length=255)
    position = models.IntegerField(default=0)  # Order columns
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='lists')
    created_at = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)
    class Meta:
        unique_together = ('project', 'position')
        indexes = [models.Index(fields=['project', 'position'])]

    def __str__(self):
        return f"{self.name} (Project: {self.project.name})"

class Team(models.Model):  # Chỉ cho enterprise projects
    name = models.CharField(max_length=255)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='teams')  
    leader = models.ForeignKey(CustomUser,null=True, blank=True, on_delete=models.SET_NULL, related_name='teams_led')  # Leader project-level khi bị admin xoá thì bị null
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('name', 'project')

    def save(self, *args, **kwargs):
        if self.project and self.project.is_personal:
            raise ValidationError("Teams chỉ cho enterprise projects.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}" + (f" (Project: {self.project.name})" if self.project else "")

class TeamMembership(models.Model):  # Through cho members với spec (project-level role)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, blank=True)  # e.g., 'backend', 'frontend', 'tester' (spec)
    joined_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'team')

    def save(self, *args, **kwargs):
        if not self.user.is_enterprise:
            raise ValidationError("Chỉ enterprise users join teams.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} in {self.team.name} as {self.role or 'member'}"

class Task(models.Model):
    STATUS_CHOICES = (('todo', 'To Do'), ('in_progress', 'In Progress'), ('done', 'Done'))
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    deadline = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')  # Có thể derive từ List.position
    priority = models.CharField(max_length=10, choices=[('low','Low'),('medium','Medium'),('high','High')], null=True, blank=True)
    list = models.ForeignKey(List, on_delete=models.CASCADE, related_name='tasks')  # Kanban position
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')  # Quick query
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_tasks')  # Leader tạo
    assignee = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_tasks')  # Leader gán
    completed_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=['project', 'status'])]

    def save(self, *args, **kwargs):
        if self.project.is_personal and self.assignee and self.assignee != self.creator:
            raise ValidationError("Personal projects không gán assignee.")
        super().save(*args, **kwargs)

    def mark_done(self, by_user):
        if self.assignee != by_user:
            raise PermissionError("Chỉ assignee mark done.")
        self.status = 'done'
        self.completed_at = timezone.now()
        self.save()
        watchers = set([self.project.leader] if self.project.leader else []) | set(CustomUser.objects.filter(role='admin', is_enterprise=True))
        for user in watchers:
            Notification.objects.create(user=user, message=f"Task '{self.name}' completed by {self.assignee.username}.")

class Comment(models.Model):  # Đơn giản: Bình luận trên task
    text = models.TextField()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

class ChecklistItem(models.Model):  # Đơn giản: Sub-tasks trên task
    name = models.CharField(max_length=255)
    is_checked = models.BooleanField(default=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='checklist_items')
    created_at = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)

class ActivityLog(models.Model):  # Optional: Log actions đơn giản
    action_type = models.CharField(max_length=50)  # e.g., 'create_project', 'assign_task'
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

class UserLockHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="lock_history")
    locked_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="locked_users")
    reason = models.TextField(blank=True, null=True)
    locked_at = models.DateTimeField(default=timezone.now)
    unlocked_at = models.DateTimeField(null=True, blank=True)
    is_current = models.BooleanField(default=True)  # Đánh dấu đây là lần khóa hiện tại (nếu đang bị khóa)

    class Meta:
        ordering = ["-locked_at"]

    def __str__(self):
        return f"{self.user.username} locked by {self.locked_by.username if self.locked_by else 'system'}"