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

class TaskSummarySerializer(serializers.Serializer):
    total = serializers.IntegerField()
    by_status = serializers.DictField(child=serializers.IntegerField())
    by_project = serializers.ListField(child=serializers.DictField())

class TaskTimeseriesPointSerializer(serializers.Serializer):
    period = serializers.CharField()
    count = serializers.IntegerField()
class TaskTimeseriesSerializer(serializers.ListSerializer):
    pass
