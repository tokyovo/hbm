import logging
from django.core.management.base import BaseCommand
from agent.tasks import get_collection_links_task  # Import the Celery task from the agent app

# Configure logger
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Run the Celery task to fetch collection links and products'

    def add_arguments(self, parser):
        parser.add_argument(
            '--collection-limit',
            type=int,
            default=3,
            help='Number of collections to process',
        )
        parser.add_argument(
            '--product-limit',
            type=int,
            default=10,
            help='Number of products to process per collection',
        )

    def handle(self, *args, **options):
        collection_limit = options['collection_limit']
        product_limit = options['product_limit']

        logger.info(f"Starting collection task with collection_limit={collection_limit}, product_limit={product_limit}")

        try:
            # Run the Celery task with the specified limits
            get_collection_links_task.delay(collection_limit=collection_limit, product_limit=product_limit)
            logger.info(f"Task triggered: Fetch {collection_limit} collections and {product_limit} products per collection")

        except Exception as e:
            # Log any errors
            logger.error(f"Error while triggering the task: {str(e)}")
