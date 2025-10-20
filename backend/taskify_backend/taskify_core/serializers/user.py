# taskify_core/serializers.py

from rest_framework import serializers
from taskify_auth.models import CustomUser
from taskify_core.models import TeamMembership

class UserSerializer(serializers.ModelSerializer):
    project_role = serializers.SerializerMethodField() # scalar cho team_id nếu truyền team_id

    project_roles = serializers.SerializerMethodField() # list tất cả roles của user (mỗi item: team_id, team_name, role)
    class Meta:
        model = CustomUser
        fields = [
            "id", "username", "email", "first_name", "last_name", "full_name","role", "is_active",
            "project_role", "project_roles",
        ]

    def get_project_role(self, obj):
        """Trả về role của user trong team được truyền team_id (nếu có)."""
        team_id = self.context.get("team_id")
        if not team_id:
            return None


        membership_map = self.context.get("membership_map")
        if membership_map is not None:
            # membership_map for team-case: user_id -> role (scalar)
            return membership_map.get(obj.id)

        # fallback (nếu view không truyền map): query DB
        m = TeamMembership.objects.filter(user=obj, team_id=team_id).first()
        return m.role if m else None

    def get_project_roles(self, obj):
        """
        Trả về danh sách role user trên tất cả team/project.
        Nếu view truyền membership_map (user_id -> list), dùng map để tránh DB hits.
        """
        membership_map = self.context.get("membership_map")
        if membership_map is not None:
            # membership_map may be user_id -> list of dicts (team_id, team_name, role)
            return membership_map.get(obj.id, [])

        # fallback: query DB (ít hiệu quả nếu nhiều user)
        memberships = TeamMembership.objects.filter(user=obj).select_related("team")
        return [
            {"team_id": m.team_id, "team_name": m.team.name if m.team else None, "role": m.role}
            for m in memberships
        ]

