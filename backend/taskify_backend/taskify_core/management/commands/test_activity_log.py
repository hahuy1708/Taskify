# taskify_core/management/commands/test_activity_log.py
from django.core.management.base import BaseCommand
from taskify_core.models import ActivityLog, Project, Task
from taskify_auth.models import CustomUser


class Command(BaseCommand):
    help = 'Test ActivityLog functionality'

    def handle(self, *args, **options):
        self.stdout.write("=== ActivityLog Test ===")
        
        # Check if ActivityLog table exists and count records
        try:
            count = ActivityLog.objects.count()
            self.stdout.write(f"✓ ActivityLog table exists with {count} records")
            
            # Show last 5 logs
            if count > 0:
                self.stdout.write("\nLast 5 activity logs:")
                for log in ActivityLog.objects.select_related('user').order_by('-timestamp')[:5]:
                    self.stdout.write(
                        f"  [{log.timestamp}] {log.action_type} by {log.user.username if log.user else 'None'}"
                    )
            else:
                self.stdout.write("⚠ No activity logs found in database")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Error accessing ActivityLog: {e}"))
            return
        
        # Check middleware and current user
        from taskify_core.middleware import get_current_user
        current = get_current_user()
        self.stdout.write(f"\n✓ Middleware get_current_user() returns: {current}")
        
        # Check if signals are imported
        try:
            from taskify_core import signals
            self.stdout.write(f"✓ Signals module imported: {signals}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Cannot import signals: {e}"))
        
        # Manual test: create a log entry
        try:
            admin = CustomUser.objects.filter(role='admin').first()
            if admin:
                ActivityLog.objects.create(
                    action_type='test_command',
                    user=admin,
                    details='{"test": "manual entry from command"}',
                )
                self.stdout.write("✓ Successfully created test log entry")
            else:
                self.stdout.write("⚠ No admin user found to test with")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Failed to create test log: {e}"))
        
        self.stdout.write("\n=== Test Complete ===")
