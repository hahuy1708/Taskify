# taskify_core/serializers/kanban.py

from rest_framework import serializers
from taskify_core.models import Project, List, Task
from taskify_auth.models import CustomUser

class NestedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'full_name', 'email']

class NestedTaskSerializer(serializers.ModelSerializer):
    assignee = NestedUserSerializer(read_only=True)
    creator = NestedUserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'name', 'description', 'deadline','status', 'priority', 'assignee', 
                  'creator', 'completed_at', 'created_at', 'updated_at',]

class ListTaskSerializer(serializers.ModelSerializer):
    tasks = NestedTaskSerializer(many=True, read_only=True) # related_name 'tasks' in List model

    class Meta:
        model = List
        fields = ['id', 'name', 'position', 'tasks']

class ProjectKanbanSerializer(serializers.ModelSerializer):
    lists = ListTaskSerializer(many=True, read_only=True) # related_name 'lists' in Project model
    leader = NestedUserSerializer(read_only=True)
    owner = NestedUserSerializer(read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'deadline', 'leader', 'owner', 'is_personal', 'is_completed','lists']
        