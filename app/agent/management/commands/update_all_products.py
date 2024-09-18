import time
import logging
from django.core.management.base import BaseCommand
from agent.models import Product
from agent.tasks import get_or_update_product_info

# Set up logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Update all products by running the get_or_update_product_info task with a delay between each product.'

    def handle(self, *args, **options):
        logger.info("Starting the update process for all products...")

        # Fetch all products from the database
        products = Product.objects.all()

        if not products.exists():
            logger.error("No products found in the database.")
            return

        # Loop through each product and call the update task
        for product in products:
            logger.info(f"Updating product: {product.title} (URL: {product.source_url})")

            try:
                # Trigger the Celery task to get or update product info
                get_or_update_product_info.delay(product.source_url)
                logger.info(f"Task triggered for product: {product.title} (URL: {product.source_url})")

            except Exception as e:
                logger.error(f"Error while triggering the task for {product.title} (URL: {product.source_url}): {e}")

            # Sleep for 10 seconds before proceeding to the next product
            logger.info("Sleeping for 10 seconds before processing the next product...")
            time.sleep(10)

        logger.info("Completed the update process for all products.")
