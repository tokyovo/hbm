import csv
import logging
from django.core.management.base import BaseCommand
from agent.models import Collection, WixProduct
from django.core.exceptions import ObjectDoesNotExist
from django.utils.text import slugify

# Set up logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Export WixProduct instances in a collection to a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('collection_pk', type=int, help='The primary key of the collection')

    def handle(self, *args, **options):
        collection_pk = options['collection_pk']

        try:
            # Fetch the collection by its primary key
            collection = Collection.objects.get(pk=collection_pk)
        except ObjectDoesNotExist:
            logger.error(f"Collection with pk {collection_pk} does not exist.")
            return

        # Fetch WixProducts associated with the collection
        wix_products = WixProduct.objects.filter(collections=collection)

        if not wix_products.exists():
            logger.warning(f"No WixProducts found for collection: {collection.title} (ID: {collection_pk})")
            return

        # Prepare the CSV file name
        filename = f"wix_products_collection_{slugify(collection.title)}.csv"

        # Define CSV headers based on the format you provided
        headers = [
            "handleId", "fieldType", "name", "description", "productImageUrl", "collection", "sku", "ribbon", "price", 
            "surcharge", "visible", "discountMode", "discountValue", "inventory", "weight", "cost",
            "productOptionName1", "productOptionType1", "productOptionDescription1", "productOptionName2",
            "productOptionType2", "productOptionDescription2", "productOptionName3", "productOptionType3",
            "productOptionDescription3", "productOptionName4", "productOptionType4", "productOptionDescription4",
            "productOptionName5", "productOptionType5", "productOptionDescription5", "productOptionName6",
            "productOptionType6", "productOptionDescription6", "additionalInfoTitle1", "additionalInfoDescription1",
            "additionalInfoTitle2", "additionalInfoDescription2", "additionalInfoTitle3", "additionalInfoDescription3",
            "additionalInfoTitle4", "additionalInfoDescription4", "additionalInfoTitle5", "additionalInfoDescription5",
            "additionalInfoTitle6", "additionalInfoDescription6", "customTextField1", "customTextCharLimit1",
            "customTextMandatory1", "brand"
        ]

        # Write CSV data
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()

            for wix_product in wix_products:
                writer.writerow({
                    "handleId": wix_product.handle_id,
                    "fieldType": wix_product.field_type,
                    "name": wix_product.name,
                    "description": wix_product.description,
                    "productImageUrl": wix_product.product_image_url,
                    "collection": ";".join([c.title for c in wix_product.collections.all()]),  # Multiple collections
                    "sku": wix_product.sku,
                    "ribbon": wix_product.ribbon,
                    "price": wix_product.price,
                    "surcharge": wix_product.surcharge,
                    "visible": wix_product.visible,
                    "discountMode": wix_product.discount_mode,
                    "discountValue": wix_product.discount_value,
                    "inventory": wix_product.inventory,
                    "weight": wix_product.weight,
                    "cost": wix_product.cost,
                    "productOptionName1": wix_product.product_option_name_1,
                    "productOptionType1": wix_product.product_option_type_1,
                    "productOptionDescription1": wix_product.product_option_description_1,
                    "productOptionName2": wix_product.product_option_name_2,
                    "productOptionType2": wix_product.product_option_type_2,
                    "productOptionDescription2": wix_product.product_option_description_2,
                    "productOptionName3": wix_product.product_option_name_3,
                    "productOptionType3": wix_product.product_option_type_3,
                    "productOptionDescription3": wix_product.product_option_description_3,
                    "productOptionName4": wix_product.product_option_name_4,
                    "productOptionType4": wix_product.product_option_type_4,
                    "productOptionDescription4": wix_product.product_option_description_4,
                    "productOptionName5": wix_product.product_option_name_5,
                    "productOptionType5": wix_product.product_option_type_5,
                    "productOptionDescription5": wix_product.product_option_description_5,
                    "productOptionName6": wix_product.product_option_name_6,
                    "productOptionType6": wix_product.product_option_type_6,
                    "productOptionDescription6": wix_product.product_option_description_6,
                    "additionalInfoTitle1": wix_product.additional_info_title_1,
                    "additionalInfoDescription1": wix_product.additional_info_description_1,
                    "additionalInfoTitle2": wix_product.additional_info_title_2,
                    "additionalInfoDescription2": wix_product.additional_info_description_2,
                    "additionalInfoTitle3": wix_product.additional_info_title_3,
                    "additionalInfoDescription3": wix_product.additional_info_description_3,
                    "additionalInfoTitle4": wix_product.additional_info_title_4,
                    "additionalInfoDescription4": wix_product.additional_info_description_4,
                    "additionalInfoTitle5": wix_product.additional_info_title_5,
                    "additionalInfoDescription5": wix_product.additional_info_description_5,
                    "additionalInfoTitle6": wix_product.additional_info_title_6,
                    "additionalInfoDescription6": wix_product.additional_info_description_6,
                    "customTextField1": wix_product.custom_text_field_1,
                    "customTextCharLimit1": wix_product.custom_text_char_limit_1,
                    "customTextMandatory1": wix_product.custom_text_mandatory_1,
                    "brand": wix_product.brand
                })

        logger.info(f"Exported {wix_products.count()} WixProduct(s) to {filename}")
