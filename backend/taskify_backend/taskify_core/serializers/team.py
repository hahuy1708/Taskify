# taskify_core/serializers/team.py

from rest_framework import serializers
from taskify_core.models import Team, Project, TeamMembership
from taskify_auth.models import CustomUser
from taskify_auth.serializers import UserSerializer

class TeamMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True) # nested
    user_id = serializers.PrimaryKeyRelatedField(
        queryset = CustomUser.objects.filter(is_enterprise=True),
        source='user',
        write_only=True,
        required=False
    )
    class Meta:
        model = TeamMembership
        fields = ['id', 'user', 'user_id', 'role', 'joined_at']
        read_only_fields=['id', 'joined_at']
    def validate_user_id(self, value):
        if not value.is_enterprise:
            raise serializers.ValidationError("Chỉ enterprise users có thể join teams")
        return value

class TeamCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)

class TeamSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(
        queryset = Project.objects.filter(is_personal=False,is_deleted=False), required=True
    )
    leader = UserSerializer(read_only=True)
    leader_id = serializers.PrimaryKeyRelatedField(
        queryset = CustomUser.objects.filter(is_enterprise=True),
        source='leader',
        required=False,
        allow_null=True
    )
    memberships = TeamMembershipSerializer(many=True, read_only=True,source='teammembership_set')
    class Meta:
        model = Team
        fields = ["id", "name", "project", "leader","leader_id","memberships" ,"is_active", "created_at", ]
        read_only_fields = ["id", "created_at"]
    
    def validate(self, attrs):
        project = attrs.get('project')
        if project.is_personal:
            raise serializers.ValidationError("Teams chỉ cho enterprise project")
        leader = attrs.get('leader')
        if leader and not leader.is_enterprise:
            raise serializers.ValidationError("Leader phải là enterprise user")
        
        return attrs