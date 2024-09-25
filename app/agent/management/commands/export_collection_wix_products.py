import csv
import logging
import os
from tqdm import tqdm
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.conf import settings
from agent.models import Collection, WixProduct  # Replace 'myapp' with the actual app name

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Export CSV files for all collections containing Wix products.'

    def export_to_csv(self, collection, wix_products):
        """
        Export the selected products and their variants to a CSV file following the Wix format.
        """
        # Slugify the collection title to use it in the filename
        filename_slug = slugify(collection.title)
        csv_filename = f'{filename_slug}_wix_products.csv'
        
        # Create a CSV file path for the collection
        csv_file_path = os.path.join(settings.MEDIA_ROOT, 'csv_exports', csv_filename)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)

        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            # Write the CSV header
            writer.writerow([
                "handleId", "fieldType", "name", "description", "productImageUrl", "collection", "sku", "ribbon", "price",
                "surcharge", "visible", "discountMode", "discountValue", "inventory", "weight", "cost",
                "productOptionName1", "productOptionType1", "productOptionDescription1", 
                "productOptionName2", "productOptionType2", "productOptionDescription2",
                "productOptionName3", "productOptionType3", "productOptionDescription3",
                "additionalInfoTitle1", "additionalInfoDescription1", "additionalInfoTitle2", 
                "additionalInfoDescription2", "brand"
            ])

            # Write the product and variant data
            for product in wix_products.filter(field_type='Product'):
                variants = WixProduct.objects.filter(handle_id=product.handle_id, field_type='Variant').order_by('pk')

                if product.price == 0.0 or any(variant.price == 0.0 for variant in variants):
                    logger.info(f"Skipping product {product.name} with handle_id {product.handle_id} due to price=0.0")
                    continue

                if not variants.exists():
                    writer.writerow([
                        product.handle_id, 'Product', product.name, product.description, product.product_image_url,
                        ";".join([c.title for c in product.collections.all()]), product.sku, product.ribbon, product.price,
                        product.surcharge, product.visible, product.discount_mode, "", 
                        product.inventory, product.weight, product.cost,
                        "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""
                    ])
                else:
                    product_and_variants = list(variants)
                    option_descriptions = [pv.product_option_description_1 for pv in product_and_variants if pv.product_option_description_1]
                    unique_option_descriptions = ";".join(option_descriptions)

                    writer.writerow([
                        product.handle_id, 'Product', product.name, product.description, product.product_image_url,
                        ";".join(set([c.title for c in product.collections.all()])), product.sku, product.ribbon, product.price,
                        product.surcharge, product.visible, product.discount_mode, "", 
                        product.inventory, product.weight, product.cost,
                        product.product_option_name_1, product.product_option_type_1, unique_option_descriptions,  
                        "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""
                    ])

                    for variant in variants:
                        writer.writerow([
                            variant.handle_id, 'Variant', None, None, None,
                            "", variant.sku, "", variant.price,
                            variant.surcharge, variant.visible, variant.discount_mode, "", 
                            variant.inventory, variant.weight, variant.cost,
                            "", "", variant.product_option_description_1,  
                            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""
                        ])

        return csv_file_path

    def handle(self, *args, **kwargs):
        # Get all collections
        collections = Collection.objects.all()

        # Loop through each collection
        for collection in tqdm(collections, desc="Exporting collections to CSV"):
            wix_products = WixProduct.objects.filter(collections=collection)
            if not wix_products.exists():
                logger.info(f"No Wix products found for collection: {collection.title}")
                continue

            # Export CSV file and save it to the collection's csv_export field
            csv_file_path = self.export_to_csv(collection, wix_products)
            collection.csv_export.name = csv_file_path.replace(settings.MEDIA_ROOT, '')
            collection.save()

            logger.info(f"CSV file saved for collection: {collection.title}")
