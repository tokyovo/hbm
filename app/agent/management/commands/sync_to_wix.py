import logging
from tqdm import tqdm
from django.core.management.base import BaseCommand
from agent.models import Product, WixProduct, Variant

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
            for product in products:
                try:
                    # Handle product variants and use the first option of the first variant for the product
                    variants = Variant.objects.filter(product=product)
                    first_variant = variants.first()

                    if first_variant:
                        option_values = first_variant.options.all()

                        # Use the first option for the main product
                        first_option = option_values.first()

                        if first_option:
                            # Update main product (first option considered as the product)
                            wix_product_defaults = {
                                'name': product.title,
                                'description': product.description,
                                'price': first_variant.price,  # Using the first variant's price
                                'product_image_url': ';'.join(set(image.url for image in product.images.all())),
                                'ribbon': 'New',  # Set ribbon to 'New'
                                'inventory': 'InStock',  # Inventory status
                                'visible': True,
                                'discount_mode': None,
                                'discount_value': 0,
                                'weight': None,
                                'cost': None,
                                'product_option_name_1': first_option.category.name,
                                #'product_option_type_1': 'COLOR' if first_option.category.name.lower() in ['color', 'colour', 'shade'] else 'DROP_DOWN',
                                'product_option_type_1': 'DROP_DOWN',
                                'product_option_description_1': first_option.value,
                            }

                            wix_product, created = WixProduct.objects.update_or_create(
                                handle_id=f"hbm_{product.pk}",  # Use 'hbm_{product.pk}' for handle_id
                                field_type='Product',
                                sku=f"hbm_{product.pk}_0",  # SKU for the main product
                                defaults=wix_product_defaults
                            )

                            wix_product.collections.set(product.collections.all())
                            wix_product.save()

                            logger.info(f"{'Created' if created else 'Updated'} WixProduct for: {product.title} (ID: {product.id})")

                    # Now handle the remaining options from the first variant and all options from subsequent variants
                    option_counter = 1  # Start after the first option

                    for variant_idx, variant in enumerate(variants):
                        for option_idx, option in enumerate(variant.options.all()):
                            # Skip the first option of the first variant (used for the product)
                            if variant_idx == 0 and option_idx == 0:
                                continue

                            option_counter += 1

                            # Sync the variant as a WixProduct with field_type 'Variant'
                            variant_wix_product_defaults = {
                                'name': f"{product.title}",
                                'description': product.description,
                                'price': variant.price,
                                'ribbon': 'New',
                                'inventory': 'InStock',
                                'visible': True,
                                'discount_mode': None,
                                'discount_value': 0,
                                'weight': None,
                                'cost': None,
                                'product_option_name_1': option.category.name,
                                #'product_option_type_1': 'COLOR' if option.category.name.lower() in ['color', 'colour', 'shade'] else 'DROP_DOWN',
                                'product_option_type_1': 'DROP_DOWN',
                                'product_option_description_1': option.value,
                            }

                            variant_wix_product, created = WixProduct.objects.update_or_create(
                                handle_id=f"hbm_{product.pk}",  # Unique handle for each option/variant
                                field_type='Variant',
                                sku=f"hbm_{product.pk}_{option_counter}",  # Unique SKU for each variant
                                defaults=variant_wix_product_defaults
                            )

                            variant_wix_product.collections.set(product.collections.all())
                            variant_wix_product.save()

                            logger.info(f"{'Created' if created else 'Updated'} WixProduct Variant for: {product.title} - Option {option_counter}")

                except Exception as e:
                    logger.error(f"Error syncing product {product.title} (ID: {product.id}): {e}")

                # Update the progress bar after each product is processed
                pbar.update(1)

        logger.info("Synchronization process completed for all products.")
