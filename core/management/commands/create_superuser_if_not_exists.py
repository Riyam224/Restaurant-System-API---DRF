import os
import traceback
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

print("🔥🔥🔥 RUNNING create_superuser_if_not_exists COMMAND 🔥🔥🔥")


class Command(BaseCommand):
    help = "Create superuser if not exists"

    def handle(self, *args, **kwargs):
        username = os.getenv("DJANGO_SUPERUSER_USERNAME")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

        self.stdout.write(f"USERNAME={username}")
        self.stdout.write(f"EMAIL={email}")
        self.stdout.write(f"PASSWORD SET={'YES' if password else 'NO'}")

        if not username or not password:
            self.stderr.write("❌ Superuser env vars NOT set")
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write("⚠️ Superuser already exists")
            return

        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
            self.stdout.write(f"✅ Superuser CREATED: {user.username}")

        except Exception as e:
            self.stderr.write("❌ FAILED TO CREATE SUPERUSER")
            self.stderr.write(str(e))
            self.stderr.write(traceback.format_exc())
