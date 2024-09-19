from django.core.management.base import BaseCommand
from django.db import connection
from agent.models import WixProduct
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Drop all records from the WixProduct table and optionally drop the table itself.'

    def add_arguments(self, parser):
        # Optional argument to drop the table completely
        parser.add_argument(
            '--drop-table',
            action='store_true',
            help='Drop the WixProduct table itself from the database schema',
        )

    def handle(self, *args, **options):
        drop_table = options['drop_table']

        # Delete all records in the WixProduct model
        logger.info("Deleting all records in WixProduct table...")
        WixProduct.objects.all().delete()
        logger.info("All records deleted from WixProduct.")

        if drop_table:
            # Drop the WixProduct table from the database schema
            logger.info("Dropping the WixProduct table from the database schema...")
            with connection.cursor() as cursor:
                cursor.execute('DROP TABLE IF EXISTS agent_wixproduct;')  # Make sure you use the correct table name
            logger.info("WixProduct table dropped from the database.")

        self.stdout.write(self.style.SUCCESS('Successfully deleted all records from WixProduct table.'))
        if drop_table:
            self.stdout.write(self.style.SUCCESS('Successfully dropped the WixProduct table from the database schema.'))
