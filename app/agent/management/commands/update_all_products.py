import time
import logging
from django.core.management.base import BaseCommand
from agent.models import Product
from agent.tasks import get_or_update_product_info

# Set up logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Update all products by running the get_or_update_product_info task and wait for each task to complete.'

    def handle(self, *args, **options):
        logger.info("Starting the update process for all products...")

        # Fetch all products from the database
        products = Product.objects.all()

        if not products.exists():
            logger.error("No products found in the database.")
            return

        # Loop through each product and call the update task, while logging the index
        for index, product in enumerate(products, start=1):
            logger.info(f"Processing product {index}/{len(products)}: {product.title} (URL: {product.source_url})")

            try:
                # Trigger the Celery task and wait for it to complete
                task = get_or_update_product_info.delay(product.source_url)
                logger.info(f"Task triggered for product {index}/{len(products)}: {product.title} (URL: {product.source_url})")

                # Wait for the task to finish
                result = task.get(timeout=300)  # Wait for up to 300 seconds (5 minutes) per task
                logger.info(f"Task completed for product {index}/{len(products)}: {product.title}")

            except Exception as e:
                logger.error(f"Error while processing product {index}/{len(products)}: {product.title} (URL: {product.source_url}): {e}")

            # Sleep for 10 seconds before proceeding to the next product
            logger.info(f"Sleeping for 10 seconds before processing the next product (index {index})...")
            time.sleep(10)

        logger.info("Completed the update process for all products.")
