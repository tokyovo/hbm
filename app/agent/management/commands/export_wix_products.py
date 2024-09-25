import csv
import os
from django.core.management.base import BaseCommand
from agent.models import WixProduct  # Replace 'myapp' with your actual app name
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Export all Wix products to a CSV file.'

    def add_arguments(self, parser):
        # Optional argument for specifying the path
        parser.add_argument('--input-path', type=str, help='Optional path to save the CSV file')

    def export_to_csv(self, wix_products, csv_file_path):
        """
        Export the given products and their variants to a CSV file following the provided format.
        """
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

    def handle(self, *args, **kwargs):
        # Fetch all Wix products
        products = WixProduct.objects.all()

        logger.info(f"Found {len(products)} products.")

        # Determine the output path for the CSV file
        input_path = kwargs.get('input_path')
        if input_path:
            csv_file_path = os.path.join(input_path, 'wix_products.csv')
        else:
            csv_file_path = 'wix_products.csv'  # Save to the current folder by default

        # Ensure the directory exists if a path is provided
        if input_path:
            os.makedirs(input_path, exist_ok=True)

        # Export products to CSV
        self.export_to_csv(WixProduct.objects, csv_file_path)
        logger.info(f"CSV file exported to {csv_file_path}")
