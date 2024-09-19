import logging
from tqdm import tqdm
from django.core.management.base import BaseCommand
from agent.models import Product, WixProduct, Collection, Variant, OptionCategory

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
                    # Sync the main product as a WixProduct
                    wix_product, created = WixProduct.objects.update_or_create(
                        handle_id=str(product.id),  # Using the Product's PK as the handle_id
                        defaults={
                            'field_type': 'Product',  # Main product
                            'name': product.title,
                            'description': product.description,
                            'price': product.price,
                            'product_image_url': ';'.join([image.url for image in product.images.all()]),
                            'sku': f"{product.id}_0",  # SKU for main product
                            'ribbon': 'sale',  # Set ribbon to 'sale'
                            'brand': None,  # Set brand if necessary
                            'inventory': 'InStock',  # Inventory status
                        }
                    )

                    # Sync the product's collections to the WixProduct
                    wix_product.collection.set(product.collections.all())
                    wix_product.save()

                    if created:
                        logger.info(f"Created WixProduct for: {product.title} (ID: {product.id})")
                    else:
                        logger.info(f"Updated WixProduct for: {product.title} (ID: {product.id})")

                    # Handle product variants
                    variants = Variant.objects.filter(product=product)
                    if variants.exists():
                        for idx, variant in enumerate(variants):
                            # Determine productOptionType
                            option_values = variant.options.all()
                            product_option_type = 'DROP_DOWN'
                            for option in option_values:
                                if option.category.name.lower() in ['color', 'colour', 'shade']:
                                    product_option_type = 'COLOR'
                                    break

                            # Sync the variant as a WixProduct with field_type 'Variant'
                            variant_wix_product, created = WixProduct.objects.update_or_create(
                                handle_id=f"{product.id}_variant_{idx}",
                                defaults={
                                    'field_type': 'Variant',
                                    'name': f"{product.title} - {variant}",  # Variant title
                                    'description': product.description,
                                    'price': variant.price,
                                    'sku': f"{product.id}_{idx + 1}",  # Variant SKU (starts from 1)
                                    'ribbon': 'sale',  # Set ribbon to 'sale'
                                    'brand': None,  # Set brand if necessary
                                    'inventory': 'InStock',  # Inventory status
                                    'productOptionType': product_option_type,
                                    'product_image_url': ';'.join([image.url for image in product.images.all()]),
                                }
                            )

                            # Sync the variant's collections to the WixProduct
                            variant_wix_product.collection.set(product.collections.all())
                            variant_wix_product.save()

                            if created:
                                logger.info(f"Created WixProduct Variant for: {product.title} - Variant {idx + 1}")
                            else:
                                logger.info(f"Updated WixProduct Variant for: {product.title} - Variant {idx + 1}")

                except Exception as e:
                    logger.error(f"Error while syncing product {product.title} (ID: {product.id}): {e}")

                # Update progress bar
                pbar.update(1)

        logger.info("Completed the synchronization process for all products to WixProduct.")
