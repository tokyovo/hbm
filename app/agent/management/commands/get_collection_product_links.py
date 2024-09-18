import logging
from django.core.management.base import BaseCommand
from agent.tasks import get_collection_links_task  # Import the Celery task from the agent app

# Configure logger
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Run the Celery task to fetch all collection links and products'

    def handle(self, *args, **options):
        logger.info("Starting collection task to fetch all collections and products")

        try:
            # Run the Celery task without any limits
            get_collection_links_task.delay()
            logger.info("Task triggered to fetch all collections and products")

        except Exception as e:
            # Log any errors
            logger.error(f"Error while triggering the task: {str(e)}")
