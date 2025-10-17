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

class UserDashboardStatsSerializer(serializers.Serializer):
    my_projects = serializers.IntegerField()
    my_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    my_productivity = serializers.FloatField()
    deltas = serializers.DictField(
        child=serializers.CharField()
    )