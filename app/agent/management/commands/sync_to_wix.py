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
            # Loop through each product and sync with WixProduct
            for product in products:
                try:
                    # Sync the main product as a WixProduct
                    wix_product, created = WixProduct.objects.update_or_create(
                        handle_id=f"hbm_{product.pk}",  # Using 'hbm_{product.pk}' as the handle_id
                        field_type='Product',  # Main product
                        sku=f"hbm_{product.id}_0",  # SKU for main product
                        defaults={
                            'name': product.title,
                            'description': product.description,
                            'price': product.price,
                            'product_image_url': ';'.join([image.url for image in product.images.all()]),
                            'ribbon': 'sale',  # Set ribbon to 'sale'
                            'inventory': 'InStock',  # Inventory status
                            'visible': True,
                            'discount_mode': None,
                            'discount_value': 0,
                            'weight': None,
                            'cost': None,
                        }
                    )

                    # Sync the product's collections to the WixProduct
                    wix_product.collections.set(product.collections.all())  # Fix here: using the many-to-many relationship
                    wix_product.save()

                    if created:
                        logger.info(f"Created WixProduct for: {product.title} (ID: {product.id})")
                    else:
                        logger.info(f"Updated WixProduct for: {product.title} (ID: {product.id})")

                    # Handle product variants, skipping the first variant
                    variants = Variant.objects.filter(product=product)
                    if variants.exists():
                        for idx, variant in enumerate(variants):
                            # Skip the first variant (assumed to be the product itself)
                            if idx == 0:
                                logger.info(f"Skipping first variant for product: {product.title} (ID: {product.id})")
                                continue

                            # Determine productOptionType
                            option_values = variant.options.all()
                            option_names = []
                            option_types = []
                            option_descriptions = []

                            # Handling multiple product options for WixProduct
                            for option in option_values:
                                # Add the option name, type, and description to the lists
                                option_names.append(option.category.name)
                                option_descriptions.append(option.value)

                                # Check for color-related options
                                if option.category.name.lower() in ['color', 'colour', 'shade']:
                                    option_types.append('COLOR')
                                else:
                                    option_types.append('DROP_DOWN')

                            # Sync the variant as a WixProduct with field_type 'Variant'
                            variant_wix_product, created = WixProduct.objects.update_or_create(
                                handle_id=f"hbm_{product.pk}",
                                field_type='Variant',
                                sku=f"hbm_{product.id}_{idx}",  # Variant SKU (starting from 1)
                                defaults={
                                    'name': f"{product.title}",  # Variant title
                                    'description': product.description,
                                    'price': variant.price,
                                    'ribbon': 'sale',  # Set ribbon to 'sale'
                                    'inventory': 'InStock',  # Inventory status
                                    'visible': True,
                                    'discount_mode': None,
                                    'discount_value': 0,
                                    'weight': None,
                                    'cost': None,
                                    'product_option_name_1': option_names[0] if len(option_names) > 0 else None,
                                    'product_option_type_1': option_types[0] if len(option_types) > 0 else None,
                                    'product_option_description_1': option_descriptions[0] if len(option_descriptions) > 0 else None,
                                    'product_option_name_2': option_names[1] if len(option_names) > 1 else None,
                                    'product_option_type_2': option_types[1] if len(option_types) > 1 else None,
                                    'product_option_description_2': option_descriptions[1] if len(option_descriptions) > 1 else None,
                                    'product_option_name_3': option_names[2] if len(option_names) > 2 else None,
                                    'product_option_type_3': option_types[2] if len(option_types) > 2 else None,
                                    'product_option_description_3': option_descriptions[2] if len(option_descriptions) > 2 else None,
                                    'product_option_name_4': option_names[3] if len(option_names) > 3 else None,
                                    'product_option_type_4': option_types[3] if len(option_types) > 3 else None,
                                    'product_option_description_4': option_descriptions[3] if len(option_descriptions) > 3 else None,
                                    'product_option_name_5': option_names[4] if len(option_names) > 4 else None,
                                    'product_option_type_5': option_types[4] if len(option_types) > 4 else None,
                                    'product_option_description_5': option_descriptions[4] if len(option_descriptions) > 4 else None,
                                    'product_option_name_6': option_names[5] if len(option_names) > 5 else None,
                                    'product_option_type_6': option_types[5] if len(option_types) > 5 else None,
                                    'product_option_description_6': option_descriptions[5] if len(option_descriptions) > 5 else None,
                                }
                            )

                            # Sync the variant's collections to the WixProduct
                            variant_wix_product.collections.set(product.collections.all())
                            variant_wix_product.save()

                            if created:
                                logger.info(f"Created WixProduct Variant for: {product.title} - Variant {idx}")
                            else:
                                logger.info(f"Updated WixProduct Variant for: {product.title} - Variant {idx}")

                except Exception as e:
                    logger.error(f"Error syncing product {product.title} (ID: {product.id}): {e}")

                # Update the progress bar after each product is processed
                pbar.update(1)

        logger.info("Synchronization process completed for all products.")
