from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class CustomUser(AbstractUser):
    ROLE_CHOICES = (('admin', 'Admin'), ('user', 'User'))  # Simplify: Chỉ admin/user global; leader/member là project-level
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    is_enterprise = models.BooleanField(default=False)  # True cho nhân viên công ty
    allow_personal = models.BooleanField(default=True)  # True cho phép tạo personal projects (ngay cả enterprise users)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)  # Soft delete
    def __str__(self):
        return f"{self.full_name or self.username} ({self.email})"

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Notif to {self.user.email} - read={self.is_read}"