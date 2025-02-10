from unittest.mock import patch

from psycopg2 import OperationalError as Psycopg2Error

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """Test commands for waiting for the database to be ready."""

    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for database if database is ready immediately."""
        # Simulate the database being ready on the first check
        patched_check.return_value = True

        # Call the management command to wait for the database
        call_command('wait_for_db')

        # Assert that the check was called once with the default database
        patched_check.assert_called_once_with(databases=['default'])
        print(f"Wait for db test: successful")

    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for database when encountering connection errors."""

        # Simulate database connection errors followed by a successful connection
        patched_check.side_effect = [Psycopg2Error] * 2 + \
            [OperationalError] * 3 + [True]

        # Call the management command to wait for the database
        call_command('wait_for_db')

        # Assert that the check was called six times in total
        self.assertEqual(patched_check.call_count, 6)

        # Assert that the final call was made with the default database
        patched_check.assert_called_with(databases=['default'])
        print(f"Wait for db delay test test: successful")
