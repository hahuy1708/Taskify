# taskify_auth/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Notification

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'username', 'full_name', 'role', 'is_enterprise', 'is_staff', 'is_active')
    list_filter = ('role', 'is_enterprise', 'is_staff', 'is_active')
    search_fields = ('email', 'username', 'full_name')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read',)
