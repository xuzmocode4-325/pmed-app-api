"""
Django command to wait for the database to be available.
"""
import time

from psycopg2 import OperationalError as Psycopg2Error

from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django wait_for_db command class. This command waits for the database to be available before proceeding."""

    def handle(self, *args, **options):
        """Entrypoint for command. Continuously checks the availability of the database and waits until it is accessible."""
        self.stdout.write('Waiting for database.')
        db_up = False
        while not db_up:
            try:
                # Attempt to check the database connection
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2Error, OperationalError):
                # If the database is not available, wait for 2 seconds before retrying
                self.stdout.write('Database unavailable, waiting 2 second...')
                time.sleep(2)

        # Once the database is available, output a success message
        self.stdout.write(self.style.SUCCESS('Database available!'))