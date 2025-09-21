# taskify_core/serializers/task.py

from rest_framework import serializers
from taskify_core.models import List, Task
from taskify_auth.models import CustomUser

class TaskSerializer(serializers.ModelSerializer):
    creator = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    assignee = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    list = serializers.PrimaryKeyRelatedField(queryset=List.objects.all())

    class Meta:
        model = Task
        fields = [
            'id', 'name', 'description', 'deadline', 'priority', 'status',
            'project', 'creator', 'assignee', 'list', 'completed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'completed_at']
