import random
from datetime import date, timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from taskify_auth.models import CustomUser, Notification


class Command(BaseCommand):
    help = "Seed 50 users + notifications for Taskify"

    def handle(self, *args, **kwargs):

        roles = ["user"]
        domains = ["gmail.com", "yahoo.com", "outlook.com"]
        names = ["An", "Bình", "Chi", "Dũng", "Hạnh", "Huy", "Lan", "Mai", "Nam", "Ngọc",
                 "Phong", "Quang", "Sơn", "Trang", "Tú", "Việt", "Vy", "Yến", "Huynh", "Elliot"]

        for i in range(2, 51):
            full_name = f"{random.choice(names)} {random.choice(names)}"
            email = f"user{i}@{random.choice(domains)}"
            username = f"user{i}"
            role = roles

            user = CustomUser.objects.create_user(
                email=email,
                username=username,
                password="password123",
                role=role,
                full_name=full_name,
                phone_number=f"09{random.randint(10000000,99999999)}",
                birth_date=date.today() - timedelta(days=random.randint(7000, 12000)),
                address=f"Số {random.randint(1,200)} Đường {random.choice(names)}",
                is_enterprise=True,
                allow_personal=random.choice([True, False]),
            )


        self.stdout.write(self.style.SUCCESS("✅ Đã tạo 50 users mẫu"))