# views.py
from django.views.generic import FormView
from django.http import HttpResponse
from .models import WixProduct, Collection
from .forms import CollectionSelectForm
import csv

class WixProductListView(FormView):
    template_name = 'agent/wixproduct_list.html'
    form_class = CollectionSelectForm

    def get_context_data(self, **kwargs):
        # Add wix_products to context, defaulting to None if not present
        context = super().get_context_data(**kwargs)
        context['wix_products'] = kwargs.get('wix_products', None)
        return context

    def form_valid(self, form):
        collection = form.cleaned_data['collection']
        wix_products = WixProduct.objects.filter(collections=collection)

        # Ensure wix_products is passed to context
        context = self.get_context_data(form=form, wix_products=wix_products, collection=collection)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        if 'export_csv' in request.POST:
            collection_id = request.POST.get('collection_id')
            collection = Collection.objects.get(id=collection_id)
            wix_products = WixProduct.objects.filter(collections=collection)

            # Export to CSV
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{collection.title}_wix_products.csv"'

            writer = csv.writer(response)
            writer.writerow([
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
            ])

            for wix_product in wix_products:
                writer.writerow([
                    wix_product.handle_id, wix_product.field_type, wix_product.name, wix_product.description, 
                    wix_product.product_image_url, ";".join([c.title for c in wix_product.collections.all()]),
                    wix_product.sku, wix_product.ribbon, wix_product.price, wix_product.surcharge, wix_product.visible,
                    wix_product.discount_mode, wix_product.discount_value, wix_product.inventory, wix_product.weight,
                    wix_product.cost, wix_product.product_option_name_1, wix_product.product_option_type_1, 
                    wix_product.product_option_description_1, wix_product.product_option_name_2,
                    wix_product.product_option_type_2, wix_product.product_option_description_2,
                    wix_product.product_option_name_3, wix_product.product_option_type_3, 
                    wix_product.product_option_description_3, wix_product.product_option_name_4,
                    wix_product.product_option_type_4, wix_product.product_option_description_4,
                    wix_product.product_option_name_5, wix_product.product_option_type_5, 
                    wix_product.product_option_description_5, wix_product.product_option_name_6,
                    wix_product.product_option_type_6, wix_product.product_option_description_6, 
                    wix_product.additional_info_title_1, wix_product.additional_info_description_1,
                    wix_product.additional_info_title_2, wix_product.additional_info_description_2,
                    wix_product.additional_info_title_3, wix_product.additional_info_description_3,
                    wix_product.additional_info_title_4, wix_product.additional_info_description_4,
                    wix_product.additional_info_title_5, wix_product.additional_info_description_5,
                    wix_product.additional_info_title_6, wix_product.additional_info_description_6,
                    wix_product.custom_text_field_1, wix_product.custom_text_char_limit_1, 
                    wix_product.custom_text_mandatory_1, wix_product.brand
                ])

            return response

        return super().post(request, *args, **kwargs)
