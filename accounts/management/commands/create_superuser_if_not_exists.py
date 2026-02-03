from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import connection
from django.conf import settings
import os

User = get_user_model()


def table_exists(table_name):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = %s
            );
            """,
            [table_name],
        )
        return cursor.fetchone()[0]


class Command(BaseCommand):
    help = "Create a superuser if it does not exist"

    def handle(self, *args, **options):
        # 1️⃣ If user table does not exist → EXIT SAFELY
        if not table_exists(User._meta.db_table):
            self.stdout.write("User table does not exist yet. Skipping.")
            return

        # 2️⃣ Optional: disable auto-creation in production
        if os.getenv("AUTO_CREATE_SUPERUSER") != "true":
            self.stdout.write("AUTO_CREATE_SUPERUSER is disabled.")
            return

        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "admin123")

        # 3️⃣ Safe query AFTER table exists
        if User.objects.filter(username=username).exists():
            self.stdout.write("Superuser already exists.")
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )

        self.stdout.write("Superuser created successfully.")
