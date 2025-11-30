# taskify_core/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import Q

from taskify_core.models import ActivityLog, Team, TeamMembership, Project, Task, Comment
from taskify_core.middleware import get_current_user


def _log(action_type: str, details: dict, actor=None):
    user = actor or get_current_user()
    if not user or not user.is_authenticated:
        return
    try:
        ActivityLog.objects.create(
            action_type=action_type,
            user=user,
            details=str(details),
            timestamp=timezone.now(),
        )
    except Exception as e:
        import traceback
        print(f"[ActivityLog ERROR] Failed to log {action_type}: {e}")
        print(traceback.format_exc())


# ===== Project signals =====
@receiver(pre_save, sender=Project)
def project_pre_save(sender, instance: Project, **kwargs):
    if instance.pk:
        try:
            instance._old = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            instance._old = None


@receiver(post_save, sender=Project)
def project_post_save(sender, instance: Project, created, **kwargs):
    actor = get_current_user()
    old = getattr(instance, "_old", None)
    if created:
        _log(
            "project_created",
            {
                "project_id": instance.id,
                "project_name": instance.name,
                "leader_id": instance.leader.id if instance.leader else None,
                "leader_name": instance.leader.username if instance.leader else None,
                "is_personal": instance.is_personal,
            },
            actor=actor,
        )
        return
    if old:
        # Marked completed
        if not old.is_completed and instance.is_completed:
            _log(
                "project_mark_completed",
                {
                    "project_id": instance.id,
                    "project_name": instance.name,
                },
                actor=actor,
            )

        # Admin updated deadline/description of project
        changed = []
        if old.deadline != instance.deadline:
            changed.append("deadline")
        if old.description != instance.description:
            changed.append("description")
        if changed and getattr(actor, "role", None) == "admin":
            _log(
                "project_updated_admin",
                {
                    "project_id": instance.id,
                    "project_name": instance.name,
                    "changed": changed,
                },
                actor=actor,
            )

        # Leader assignment changed
        if old.leader_id != instance.leader_id and instance.leader_id:
            _log(
                "project_leader_assigned",
                {
                    "project_id": instance.id,
                    "project_name": instance.name,
                    "leader_id": instance.leader.id if instance.leader else None,
                    "leader_name": instance.leader.username if instance.leader else None,
                },
                actor=actor,
            )


# ===== Team signals =====
@receiver(post_save, sender=Team)
def team_post_save(sender, instance: Team, created, **kwargs):
    if created:
        actor = get_current_user()
        _log(
            "team_created",
            {
                "team_id": instance.id,
                "team_name": instance.name,
                "project_id": instance.project.id if instance.project else None,
                "project_name": instance.project.name if instance.project else None,
                "leader_id": instance.leader.id if instance.leader else None,
            },
            actor=actor,
        )


@receiver(post_save, sender=TeamMembership)
def team_membership_post_save(sender, instance: TeamMembership, created, **kwargs):
    actor = get_current_user()
    if created:
        # When a member is added to a team
        _log(
            "team_member_added",
            {
                "team_id": instance.team.id,
                "team_name": instance.team.name,
                "member_id": instance.user.id,
                "member_name": instance.user.username,
            },
            actor=actor,
        )


# ===== Task signals =====
@receiver(pre_save, sender=Task)
def task_pre_save(sender, instance: Task, **kwargs):
    if instance.pk:
        try:
            instance._old = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            instance._old = None


@receiver(post_save, sender=Task)
def task_post_save(sender, instance: Task, created, **kwargs):
    actor = get_current_user()
    old = getattr(instance, "_old", None)

    if created:
        return

    if old:
        # Member A done task B
        if old.status != "done" and instance.status == "done":
            _log(
                "task_done",
                {
                    "task_id": instance.id,
                    "task_name": instance.name,
                    "project_id": instance.project.id if instance.project else None,
                    "project_name": instance.project.name if instance.project else None,
                    "assignee_id": instance.assignee.id if instance.assignee else None,
                },
                actor=actor,
            )

        # Member A moved task to in_progress
        if old.status != "in_progress" and instance.status == "in_progress":
            _log(
                "task_moved_inprogress",
                {
                    "task_id": instance.id,
                    "task_name": instance.name,
                    "project_id": instance.project.id if instance.project else None,
                    "project_name": instance.project.name if instance.project else None,
                    "from": old.status,
                    "to": instance.status,
                },
                actor=actor,
            )

        # Leader assigned task to member (assignee changed)
        if old.assignee_id != instance.assignee_id and instance.assignee_id:
            _log(
                "task_assigned",
                {
                    "task_id": instance.id,
                    "task_name": instance.name,
                    "assignee_id": instance.assignee_id,
                    "assignee_name": instance.assignee.username if instance.assignee else None,
                },
                actor=actor,
            )

        # Leader updated deadlines/description
        changed = []
        if old.deadline != instance.deadline:
            changed.append("deadline")
        if old.description != instance.description:
            changed.append("description")
        if changed:
            _log(
                "task_updated",
                {
                    "task_id": instance.id,
                    "task_name": instance.name,
                    "changed": changed,
                },
                actor=actor,
            )


# ===== Comment signals =====
@receiver(post_save, sender=Comment)
def comment_post_save(sender, instance: Comment, created, **kwargs):
    if not created:
        return
    actor = get_current_user()
    _log(
        "task_commented",
        {
            "task_id": instance.task.id if instance.task_id else None,
            "task_name": instance.task.name if instance.task_id else None,
            "project_id": instance.task.project.id if instance.task_id and instance.task.project_id else None,
            "project_name": instance.task.project.name if instance.task_id and instance.task.project_id else None,
            "comment_id": instance.id,
        },
        actor=actor,
    )
