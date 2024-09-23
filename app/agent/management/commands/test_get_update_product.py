import logging
from django.core.management.base import BaseCommand
from agent.models import Product
from agent.tasks import get_or_update_product_info

# Set up logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fetch a product by primary key (pk) from the database and run get_or_update_product_info for testing.'

    def add_arguments(self, parser):
        # Add an argument to accept the product pk
        parser.add_argument('pk', type=int, help='The primary key of the product to fetch.')

    def handle(self, *args, **options):
        product_pk = options['pk']
        logger.info(f"Starting the test for get_or_update_product_info for product with pk={product_pk}...")

        # Fetch the product from the database using the provided pk
        try:
            product = Product.objects.get(pk=product_pk)
        except Product.DoesNotExist:
            logger.error(f"No product found with pk={product_pk}.")
            return

        logger.info(f"Selected product: {product.pk} - {product.title} (URL: {product.source_url})")

        try:
            # Trigger the Celery task to get or update product info
            get_or_update_product_info.delay(product.source_url)
            logger.info(f"Task triggered for product: {product.pk} (URL: {product.source_url})")

        except Exception as e:
            logger.error(f"Error while triggering the task for product {product.pk} (URL: {product.source_url}): {e}")
