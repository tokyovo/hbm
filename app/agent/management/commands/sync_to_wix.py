import logging
from tqdm import tqdm
from django.core.management.base import BaseCommand
from agent.models import Product, WixProduct, Collection

# Set up logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Sync all Product instances to WixProduct'

    def handle(self, *args, **options):
        logger.info("Starting the synchronization process for all products to WixProduct...")

        # Fetch all products from the database
        products = Product.objects.all()

        if not products.exists():
            logger.error("No products found in the database.")
            return

        # Initialize tqdm progress bar
        with tqdm(total=products.count(), desc="Syncing Products", unit="product") as pbar:
            # Loop through each product and sync with WixProduct
            for product in products:
                try:
                    # Create or update the corresponding WixProduct entry
                    wix_product, created = WixProduct.objects.update_or_create(
                        handle_id=str(product.id),  # Using the Product's PK as the handle_id
                        defaults={
                            'field_type': 'Product',  # Always 'Product', change if needed for variants
                            'name': product.title,
                            'description': product.description,
                            'price': product.price,
                            'product_image_url': ';'.join([image.url for image in product.images.all()]),
                            'sku': None,  # Adjust SKU if needed
                            'ribbon': None,  # Set ribbon if necessary
                            'brand': None,  # Set brand if necessary
                        }
                    )

                    # Sync the product's collections to the WixProduct
                    wix_product.collection.set(product.collections.all())

                    # Save the WixProduct instance
                    wix_product.save()

                    if created:
                        logger.info(f"Created WixProduct for: {product.title} (ID: {product.id})")
                    else:
                        logger.info(f"Updated WixProduct for: {product.title} (ID: {product.id})")

                except Exception as e:
                    logger.error(f"Error while syncing product {product.title} (ID: {product.id}): {e}")

                # Update progress bar
                pbar.update(1)

        logger.info("Completed the synchronization process for all products to WixProduct.")
