import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Creates or updates the Django admin account.

    This command is used when the project is deployed so an
    administrator account is automatically available without
    creating it manually.
    """

    help = "Create or update the Django admin account from environment variables"

    def handle(self, *args, **options):

        # Get the admin login details from the
        # environment variables.
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        # Stop if the username or password has not been provided.
        if not username or not password:
            self.stdout.write(
                self.style.WARNING(
                    "Admin account was not created because "
                    "DJANGO_SUPERUSER_USERNAME or "
                    "DJANGO_SUPERUSER_PASSWORD is missing."
                )
            )
            return

        User = get_user_model()

        # Create the admin account if it doesn't exist.
        # Otherwise, use the existing account.
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email or "",
                "is_staff": True,
                "is_superuser": True,
            },
        )

        # Update the account details each time the command runs
        # so the credentials always match the environment variables.
        user.email = email or user.email
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        # Show whether a new account was created
        # or an existing one was updated.
        if created:
            message = f"Admin account '{username}' created successfully."
        else:
            message = f"Admin account '{username}' updated successfully."

        self.stdout.write(self.style.SUCCESS(message))