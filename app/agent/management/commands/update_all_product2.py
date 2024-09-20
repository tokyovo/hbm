import time
import logging
import subprocess
from django.core.management.base import BaseCommand
from agent.models import Product
from agent.tasks import get_or_update_product_info

# Set up logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Update all products by running the get_or_update_product_info task and wait for each task to complete.'

    def kill_chrome_processes(self):
        """Kill all Chrome and ChromeDriver processes."""
        try:
            subprocess.run(["pkill", "-f", "chrome"], check=True)
            subprocess.run(["pkill", "-f", "chromedriver"], check=True)
            logger.info("Killed all existing Chrome and ChromeDriver processes.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error killing Chrome/ChromeDriver processes: {e}")

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

            # Every 100 products, kill all existing Chrome and ChromeDriver processes
            if index % 100 == 0:
                logger.info(f"Killing all Chrome and ChromeDriver processes after processing {index} products.")
                self.kill_chrome_processes()

            # Sleep for 10 seconds before proceeding to the next product
            logger.info(f"Sleeping for 10 seconds before processing the next product (index {index})...")
            time.sleep(10)

        logger.info("Completed the update process for all products.")
