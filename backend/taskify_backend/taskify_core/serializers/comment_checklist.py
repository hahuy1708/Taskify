# taskify_core?serializers/comment_checklist.py

from rest_framework import serializers
from taskify_core.models import Comment, ChecklistItem, Task
from taskify_auth.serializers import UserSerializer

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # Nested user info

    class Meta:
        model = Comment
        fields = ['id', 'text', 'user', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Auto set user = request.user ở view/service
        return super().create(validated_data)

class ChecklistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChecklistItem
        fields = ['id', 'name', 'is_checked', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        return super().create(validated_data)