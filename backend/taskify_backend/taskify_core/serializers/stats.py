from rest_framework import serializers

class StatsMetricSerializer(serializers.Serializer):
    value = serializers.IntegerField()
    delta = serializers.CharField()

class AdminDashboardStatsSerializer(serializers.Serializer):
    total_projects = serializers.IntegerField()
    active_users = serializers.IntegerField()
    tasks_completed = serializers.IntegerField()
    productivity = serializers.FloatField()
    deltas = serializers.DictField(
        child=serializers.CharField(),
        default={
            'projects': '0%',
            'users': '0%',
            'tasks': '0%',
            'productivity': '0%'
        }
    )
    urgent_issues = serializers.ListField(child=serializers.DictField(), default=list)

class UserDashboardStatsSerializer(serializers.Serializer):
    assigned_projects = serializers.IntegerField()
    assigned_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    productivity = serializers.FloatField()
    upcoming_deadlines = serializers.ListField(child=serializers.DictField(), default=list)

# ===== Reports =====
# Overview 
class ProjectStatusDistributionSerializer(serializers.Serializer):
    active = serializers.IntegerField()
    completed = serializers.IntegerField()
    overdue = serializers.IntegerField()

class TaskPriorityDistributionSerializer(serializers.Serializer):
    high = serializers.IntegerField()
    medium = serializers.IntegerField()
    low = serializers.IntegerField()

class ProjectCompletionBarItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    done = serializers.IntegerField()
    remaining = serializers.IntegerField()
    total = serializers.IntegerField()

class ReportsOverviewSerializer(serializers.Serializer):
    project_status = ProjectStatusDistributionSerializer()
    task_priority = TaskPriorityDistributionSerializer()
    completion_bars = serializers.ListField(child=ProjectCompletionBarItemSerializer())

# Members - Workload
class TopContributorsSerializer(serializers.Serializer):
    # top 5 members by completed tasks
    member_id = serializers.IntegerField() 
    member_name = serializers.CharField()
    completed_tasks = serializers.IntegerField()

class TeamWorkloadSerializer(serializers.Serializer):
    # active task per team
    team_id = serializers.IntegerField()
    team_name = serializers.CharField()
    active_tasks = serializers.IntegerField()
class ProjectByLeaderSerializer(serializers.Serializer):
    # top 5 leaders by number of projects
    leader_id = serializers.IntegerField()
    leader_name = serializers.CharField()
    project_count = serializers.IntegerField()

class ReportsMembersWorkloadSerializer(serializers.Serializer):
    team_workload = serializers.ListField(child=TeamWorkloadSerializer())
    top_contributors = serializers.ListField(child=TopContributorsSerializer())
    projects_by_leader = serializers.ListField(child=ProjectByLeaderSerializer())

