"""
Idempotent admin-bootstrap command for hosts without shell access
(e.g. Render's free tier). Reads credentials from environment variables
and creates (or leaves untouched) one ADMIN superuser.

Run automatically from build.sh on every deploy — safe to run repeatedly:
if the username already exists, it does nothing.

Required env vars: ADMIN_USERNAME, ADMIN_EMAIL, ADMIN_PASSWORD
"""
import os
from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = "Creates a default ADMIN superuser from ADMIN_USERNAME/ADMIN_EMAIL/ADMIN_PASSWORD env vars, if it doesn't already exist."

    def handle(self, *args, **options):
        username = os.environ.get('ADMIN_USERNAME')
        email = os.environ.get('ADMIN_EMAIL', '')
        password = os.environ.get('ADMIN_PASSWORD')

        if not username or not password:
            self.stdout.write(self.style.WARNING(
                "ADMIN_USERNAME / ADMIN_PASSWORD not set — skipping admin bootstrap."
            ))
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.SUCCESS(
                f"Admin user '{username}' already exists — nothing to do."
            ))
            return

        User.objects.create_superuser(
            username=username, email=email, password=password, role=User.Role.ADMIN,
        )
        self.stdout.write(self.style.SUCCESS(
            f"Created admin user '{username}' with role=ADMIN."
        ))
