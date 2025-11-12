# taskify_core/serializers/task.py

from rest_framework import serializers
from taskify_core.models import Comment, List, Task, Project, ChecklistItem
from taskify_auth.models import CustomUser


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "full_name", "email"]
        read_only_fields = fields


class ProjectMiniSerializer(serializers.ModelSerializer):
    leader = SimpleUserSerializer(read_only=True)
    class Meta:
        model = Project
        fields = ["id", "name", "is_personal", "leader"]
        read_only_fields = fields

class SimpleCommentSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)
    class Meta:
        model = Comment
        fields = ["id", "text", "user", "created_at", "updated_at"]
        read_only_fields = fields

class SimpleChecklistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChecklistItem
        fields = ["id", "name", "is_checked", "created_at", "is_deleted"]
        read_only_fields = ["id", "created_at"]

class TaskSerializer(serializers.ModelSerializer):
    # Output nested info for better UX; views use this serializer for responses only
    creator = SimpleUserSerializer(read_only=True)
    assignee = SimpleUserSerializer(read_only=True)
    project = ProjectMiniSerializer(read_only=True)
    list = serializers.PrimaryKeyRelatedField(queryset=List.objects.all())

    class Meta:
        model = Task
        fields = [
            "id",
            "name",
            "description",
            "deadline",
            "priority",
            "status",
            "project",
            "creator",
            "is_deleted",
            "assignee",
            "list",
            "completed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "completed_at", "project", "creator", "assignee"]


class TaskDetailSerializer(serializers.ModelSerializer):
    creator = SimpleUserSerializer(read_only=True)
    assignee = SimpleUserSerializer(read_only=True)
    project = ProjectMiniSerializer(read_only=True)
    list = serializers.PrimaryKeyRelatedField(queryset=List.objects.all())
    comments = SimpleCommentSerializer(many=True, read_only=True)
    checklist_items = SimpleChecklistItemSerializer(many=True, read_only=True)
    class Meta:
        model = Task
        fields = [
            "id",
            "name",
            "description",
            "deadline",
            "priority",
            "status",
            "project",
            "creator",
            "is_deleted",
            "assignee",
            "list",
            "comments",
            "checklist_items",
            "completed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "completed_at", "project", "creator", "assignee", "comments", "checklist_items"]

class UpdateTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'name', 'description', 'deadline', 'priority',
            'assignee', 'list', 'is_deleted'
        ]
        # Allow partial updates and nullable fields where applicable
        extra_kwargs = {
            'name': {'required': False},
            'description': {'required': False, 'allow_blank': True, 'allow_null': True},
            'deadline': {'required': False, 'allow_null': True},
            'priority': {'required': False},
            'assignee': {'required': False, 'allow_null': True},
            'list': {'required': False},
            'is_deleted': {'required': False},
        }