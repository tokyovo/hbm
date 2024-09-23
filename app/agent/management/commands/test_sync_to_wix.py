import logging
from tqdm import tqdm
from django.core.management.base import BaseCommand
from agent.models import Product, WixProduct, Collection, Variant, OptionCategory

# Set up logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Sync a limited number of Product instances to WixProduct'

    def handle(self, *args, **options):
        logger.info("Starting the synchronization process for a single product to WixProduct...")

        # Fetch only the first product from the database
        product = Product.objects.first()

        if not product:
            logger.error("No products found in the database.")
            return

        # Initialize tqdm progress bar with total 1 product
        with tqdm(total=1, desc="Syncing Product", unit="product") as pbar:
            try:
                # Ensure the product has a collection
                if product.collections.exists():
                    collection = product.collections.first()  # Get the first collection
                else:
                    # Optionally assign a default collection
                    collection, _ = Collection.objects.get_or_create(title="Default Collection")
                    logger.warning(f"Assigned default collection to product {product.title} (ID: {product.id})")

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
                        'inventory': 'InStock',  # Inventory status
                        'visible': True,
                        'discount_mode': None,
                        'discount_value': 0,
                        'weight': None,
                        'cost': None,
                        'collection_id': collection.id  # Set the collection_id
                    }
                )

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
                            handle_id=f"{product.id}_variant_{idx}",
                            defaults={
                                'field_type': 'Variant',
                                'name': f"{product.title} - {variant}",  # Variant title
                                'description': product.description,
                                'price': variant.price,
                                'sku': f"{product.id}_{idx + 1}",  # Variant SKU (starts from 1)
                                'ribbon': 'sale',  # Set ribbon to 'sale'
                                'inventory': 'InStock',  # Inventory status
                                'visible': True,
                                'discount_mode': None,
                                'discount_value': 0,
                                'weight': None,
                                'cost': None,
                                'collection_id': collection.id,  # Set the collection_id for the variant
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

                        if created:
                            logger.info(f"Created WixProduct Variant for: {product.title} - Variant {idx + 1}")
                        else:
                            logger.info(f"Updated WixProduct Variant for: {product.title} - Variant {idx + 1}")

            except Exception as e:
                logger.error(f"Error while syncing product {product.title} (ID: {product.id}): {e}")

            # Update progress bar
            pbar.update(1)

        logger.info("Completed the synchronization process for the selected product to WixProduct.")
