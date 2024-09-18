import random
import logging
from django.core.management.base import BaseCommand
from agent.models import Product
from agent.tasks import get_or_update_product_info

# Set up logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fetch a random product from the database and run get_or_update_product_info for testing.'

    def handle(self, *args, **options):
        logger.info("Starting the test for get_or_update_product_info...")

        # Fetch all product source URLs from the database
        product_count = Product.objects.count()

        if product_count == 0:
            logger.error("No products found in the database.")
            return

        # Get a random product from the database
        random_product = Product.objects.all()[random.randint(0, product_count - 1)]

        logger.info(f"Selected random product: {random_product.title} (URL: {random_product.source_url})")

        try:
            # Trigger the Celery task to get or update product info
            get_or_update_product_info.delay(random_product.source_url)
            logger.info(f"Task triggered for product: {random_product.source_url}")

        except Exception as e:
            logger.error(f"Error while triggering the task for {random_product.source_url}: {e}")
