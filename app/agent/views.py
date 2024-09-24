import csv
from django.http import HttpResponse
from django.views.generic import TemplateView
from .forms import CollectionSelectForm
from .models import WixProduct, Collection

class WixProductListView(TemplateView):
    template_name = 'agent/wixproduct_list.html'

    def get(self, request, *args, **kwargs):
        form = CollectionSelectForm()
        return self.render_to_response({'form': form})

    def post(self, request, *args, **kwargs):
        form = CollectionSelectForm(request.POST)
        if form.is_valid():
            collection = form.cleaned_data['collection']
            wix_products = WixProduct.objects.filter(collections=collection)

            # Check if export to CSV
            if 'export_csv' in request.POST:
                return self.export_to_csv(collection, wix_products)

            # Pass the selected collection and products back to the template
            return self.render_to_response({
                'form': form,
                'wix_products': wix_products,
                'collection': collection
            })

        # If form is not valid, render the form again
        return self.render_to_response({'form': form})

    def export_to_csv(self, collection, wix_products):
        """
        Export the selected products and their variants to a CSV file following the Wix format.
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{collection.title}_wix_products.csv"'

        writer = csv.writer(response)
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

        for product in wix_products:
            # Write the main product row
            writer.writerow([
                product.handle_id, 'Product', product.name, product.description, product.product_image_url,
                ";".join([c.title for c in product.collections.all()]), product.sku, product.ribbon, product.price,
                product.surcharge, product.visible, product.discount_mode, product.discount_value, 
                product.inventory, product.weight, product.cost,
                product.product_option_name_1, product.product_option_type_1, product.product_option_description_1,
                product.product_option_name_2, product.product_option_type_2, product.product_option_description_2,
                product.product_option_name_3, product.product_option_type_3, product.product_option_description_3,
                product.product_option_name_4, product.product_option_type_4, product.product_option_description_4,
                product.product_option_name_5, product.product_option_type_5, product.product_option_description_5,
                product.product_option_name_6, product.product_option_type_6, product.product_option_description_6,
                product.additional_info_title_1, product.additional_info_description_1, 
                product.additional_info_title_2, product.additional_info_description_2, 
                product.additional_info_title_3, product.additional_info_description_3,
                product.additional_info_title_4, product.additional_info_description_4,
                product.additional_info_title_5, product.additional_info_description_5,
                product.additional_info_title_6, product.additional_info_description_6,
                product.custom_text_field_1, product.custom_text_char_limit_1, 
                product.custom_text_mandatory_1, product.brand
            ])

            # Write variants associated with the product
            variants = WixProduct.objects.filter(handle_id=product.handle_id, field_type='Variant')
            for variant in variants:
                writer.writerow([
                    variant.handle_id, 'Variant', None, None, None,
                    ";".join([c.title for c in variant.collections.all()]), variant.sku, variant.ribbon, variant.price,
                    variant.surcharge, variant.visible, variant.discount_mode, variant.discount_value, 
                    variant.inventory, variant.weight, variant.cost,
                    variant.product_option_name_1, variant.product_option_type_1, variant.product_option_description_1,
                    variant.product_option_name_2, variant.product_option_type_2, variant.product_option_description_2,
                    variant.product_option_name_3, variant.product_option_type_3, variant.product_option_description_3,
                    variant.product_option_name_4, variant.product_option_type_4, variant.product_option_description_4,
                    variant.product_option_name_5, variant.product_option_type_5, variant.product_option_description_5,
                    variant.product_option_name_6, variant.product_option_type_6, variant.product_option_description_6,
                    variant.additional_info_title_1, variant.additional_info_description_1,
                    variant.additional_info_title_2, variant.additional_info_description_2,
                    variant.additional_info_title_3, variant.additional_info_description_3,
                    variant.additional_info_title_4, variant.additional_info_description_4,
                    variant.additional_info_title_5, variant.additional_info_description_5,
                    variant.additional_info_title_6, variant.additional_info_description_6,
                    variant.custom_text_field_1, variant.custom_text_char_limit_1, 
                    variant.custom_text_mandatory_1, variant.brand
                ])

        return response
