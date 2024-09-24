import logging
from django.http import HttpResponse
from django.views.generic import TemplateView
from .forms import CollectionSelectForm
from .models import WixProduct, Collection
import csv

# Set up logging
logger = logging.getLogger(__name__)

class WixProductListView(TemplateView):
    template_name = 'agent/wixproduct_list.html'

    def get(self, request, *args, **kwargs):
        logger.debug("GET request received.")
        form = CollectionSelectForm()
        logger.debug("Empty form initialized.")
        return self.render_to_response({'form': form, 'wix_products': None, 'collection': None})

    def post(self, request, *args, **kwargs):
        logger.debug("POST request received.")
        form = CollectionSelectForm(request.POST)
        wix_products = None
        collection = None

        logger.debug("Form submitted with POST data: %s", request.POST)

        if form.is_valid():
            logger.debug("Form is valid.")
            collection = form.cleaned_data['collection']
            logger.debug("Collection selected: %s (ID: %s)", collection.title, collection.id)

            wix_products = WixProduct.objects.filter(collections=collection)
            logger.debug("Wix products retrieved: %d products found.", wix_products.count())

            # Check if export to CSV button was pressed
            if 'export_csv' in request.POST:
                logger.debug("Export to CSV button clicked.")
                logger.debug("Request POST data during export: %s", request.POST)  # Log the entire POST data
                logger.debug("Collection passed for export: %s (ID: %s)", collection.title, collection.id)
                return self.export_to_csv(collection, wix_products)
        else:
            # Handle the case where 'export_csv' is clicked but the form is not valid
            logger.debug("Form is invalid. Errors: %s", form.errors)

            if 'export_csv' in request.POST:
                logger.debug("Export to CSV attempted with invalid form data.")
                logger.debug("Request POST data during failed export: %s", request.POST)

            if 'export_csv' in request.POST and 'collection_id' in request.POST:
                collection_id = request.POST.get('collection_id')
                collection = Collection.objects.get(id=collection_id)
                wix_products = WixProduct.objects.filter(collections=collection)

                logger.debug("Exporting products to CSV for collection: %s", collection.title)
                return self.export_to_csv(collection, wix_products)

        # Pass the form and wix_products to the template
        logger.debug("Rendering response with form, wix_products, and collection.")
        return self.render_to_response({
            'form': form,
            'wix_products': wix_products,
            'collection': collection  # Add collection to the context
        })

    def export_to_csv(self, collection, wix_products):
        """
        Export the selected products and their variants to a CSV file following the Wix format.
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{collection.title}_wix_products.csv"'

        writer = csv.writer(response)
        
        # Write the CSV header
        writer.writerow([
            "handleId", "fieldType", "name", "description", "productImageUrl", "collection", "sku", "ribbon", "price",
            "surcharge", "visible", "discountMode", "discountValue", "inventory", "weight", "cost",
            "productOptionName1", "productOptionType1", "productOptionDescription1", 
            "productOptionName2", "productOptionType2", "productOptionDescription2",
            "productOptionName3", "productOptionType3", "productOptionDescription3",
            "productOptionName4", "productOptionType4", "productOptionDescription4",
            "productOptionName5", "productOptionType5", "productOptionDescription5",
            "productOptionName6", "productOptionType6", "productOptionDescription6",
            "additionalInfoTitle1", "additionalInfoDescription1", "additionalInfoTitle2", 
            "additionalInfoDescription2", "additionalInfoTitle3", "additionalInfoDescription3", 
            "additionalInfoTitle4", "additionalInfoDescription4", "additionalInfoTitle5", 
            "additionalInfoDescription5", "additionalInfoTitle6", "additionalInfoDescription6", 
            "customTextField1", "customTextCharLimit1", "customTextMandatory1", "brand"
        ])

        # Write the product and variant data
        for product in wix_products.filter(field_type='Product'):
            # Get all variants for this product (same handle_id)
            variants = WixProduct.objects.filter(handle_id=product.handle_id, field_type='Variant').order_by('pk')

            # If no variants, write only the product details up to 'cost'
            if not variants.exists():
                writer.writerow([
                    product.handle_id, 'Product', product.name, product.description, product.product_image_url,
                    ";".join([c.title for c in product.collections.all()]), product.sku, product.ribbon, product.price,
                    product.surcharge, product.visible, product.discount_mode, product.discount_value, 
                    product.inventory, product.weight, product.cost,  # Fill remaining columns with empty strings
                    "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""
                ])
            else:
                # Create a unique list of option descriptions from the product and variants
                product_and_variants = list(variants)
                option_descriptions = [pv.product_option_description_1 for pv in product_and_variants if pv.product_option_description_1]
                unique_option_descriptions = ";".join(option_descriptions)

                # Write product row with combined option descriptions
                writer.writerow([
                    product.handle_id, 'Product', product.name, product.description, product.product_image_url,
                    ";".join(set([c.title for c in product.collections.all()])), product.sku, product.ribbon, product.price,
                    product.surcharge, product.visible, product.discount_mode, product.discount_value, 
                    product.inventory, product.weight, product.cost,
                    product.product_option_name_1, product.product_option_type_1, unique_option_descriptions,  # unique list of option descriptions
                    "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""
                ])

                # Write variants for the product
                for variant in variants:
                    writer.writerow([
                        variant.handle_id, 'Variant', None, None, None,
                        "", variant.sku, "", variant.price,
                        variant.surcharge, variant.visible, variant.discount_mode, variant.discount_value, 
                        variant.inventory, variant.weight, variant.cost,
                        "", "", variant.product_option_description_1,  # Empty name/type, variant description
                        "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""
                    ])

        return response
