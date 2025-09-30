# taskify_core/serializers/project.py
from rest_framework import serializers
from taskify_core.models import Project
from taskify_auth.models import CustomUser

class ProjectSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), required=False, allow_null=True
    )
    leader = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Project
        fields = (
            "id", "name", "description", "deadline", "owner", "leader",
            "is_personal", "is_completed", "is_deleted",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "is_deleted")

class UpdateProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
            "name", "description", 'owner', "deadline", "leader", "is_personal", "is_completed", "is_deleted"
        )
        extra_kwargs = {field: {'required': False} for field in fields}
