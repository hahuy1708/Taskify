# taskify_core/serializers/project.py
from rest_framework import serializers
from taskify_core.models import Project
from taskify_auth.models import CustomUser

class ProjectSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), required=False, allow_null=True
    )
    # leader = serializers.PrimaryKeyRelatedField(
    #     queryset=CustomUser.objects.all(), required=False, allow_null=True
    # )
    leader = serializers.SerializerMethodField()
    member_count = serializers.IntegerField(read_only=True)
    progress = serializers.FloatField(read_only=True)

    deadline = serializers.DateTimeField(format="%Y-%m-%d", required=False, allow_null=True)
    class Meta:
        model = Project
        fields = (
            "id", "name", "description", "deadline", "owner", "leader",
            "is_personal", "is_completed", "is_deleted",
            "created_at", "updated_at",
            "member_count", "progress"
        )
        read_only_fields = ("id", "created_at", "updated_at", "is_deleted", "member_count", "progress")
    def get_leader(self, obj):
        if obj.leader:
            return {
            "id": obj.leader.id,
            "name": obj.leader.full_name or obj.leader.username
        }
        return None

class UpdateProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
            "name", "description", 'owner', "deadline", "leader", "is_personal", "is_completed", "is_deleted"
        )
        extra_kwargs = {field: {'required': False} for field in fields}
