import logging
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Collection, Product, Variant, Image, OptionCategory, OptionValue, WixProduct

logger = logging.getLogger(__name__)

class VariantInline(admin.TabularInline):
    model = Variant
    extra = 1
    fields = ['price', 'get_options']
    readonly_fields = ['get_options']

    def get_options(self, obj):
        logger.debug("VariantInline: get_options called")
        return ", ".join([str(option) for option in obj.options.all()])

    get_options.short_description = 'Options'


class ImageInline(admin.TabularInline):
    model = Image
    extra = 1
    fields = ['url', 'alt_text']


class ProductInlineInCollection(admin.TabularInline):
    model = Product.collections.through
    extra = 0
    fields = ['get_product_link']
    readonly_fields = ['get_product_link']

    def get_product_link(self, obj):
        product = obj.product
        url = reverse('admin:agent_product_change', args=[product.id])
        logger.debug(f"ProductInlineInCollection: get_product_link for product {product.title}")
        return format_html('<a href="{}">{}</a>', url, product.title)

    get_product_link.short_description = 'Product'


class WixProductInline(admin.TabularInline):
    model = WixProduct.collections.through  # This links the many-to-many relationship
    extra = 0
    fields = ['get_wixproduct_link']
    readonly_fields = ['get_wixproduct_link']

    def get_wixproduct_link(self, obj):
        wixproduct = obj.wixproduct
        url = reverse('admin:agent_wixproduct_change', args=[wixproduct.id])
        logger.debug(f"WixProductInline: get_wixproduct_link for WixProduct {wixproduct.name}")
        return format_html('<a href="{}">{}</a>', url, wixproduct.name)

    get_wixproduct_link.short_description = 'Wix Product'


class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'price', 'get_collections', 'allow_update', 'created_at', 'updated_at']
    search_fields = ['title', 'description']
    list_filter = ['allow_update', 'created_at', 'updated_at']
    inlines = [VariantInline, ImageInline]

    def get_collections(self, obj):
        logger.debug(f"Fetching collections for product {obj.id}")
        collections = obj.collections.all()
        links = [format_html('<a href="{}">{}</a>', self.get_admin_url(c), c.title) for c in collections]
        return format_html(", ".join(links))

    get_collections.short_description = 'Collections'

    def get_admin_url(self, obj):
        url = reverse('admin:agent_collection_change', args=[obj.id])
        logger.debug(f"Generated admin URL: {url}")
        return url


class ProductInlineInCollection(admin.TabularInline):
    model = Product.collections.through
    extra = 0
    fields = ['get_product_link']
    readonly_fields = ['get_product_link']

    def get_product_link(self, obj):
        product = obj.product
        url = reverse('admin:agent_product_change', args=[product.id])
        logger.debug(f"ProductInlineInCollection: get_product_link for product {product.title}")
        return format_html('<a href="{}">{}</a>', url, product.title)

    get_product_link.short_description = 'Product'


class CollectionAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'description', 'get_product_count']
    search_fields = ['title', 'description']
    inlines = [ProductInlineInCollection]  # Inline for products in the collection

    # Function to count products in a collection
    def get_product_count(self, obj):
        return obj.products.count()

    get_product_count.short_description = 'Total Products'

    # Custom export action to export the products in a collection to CSV
    def export_to_csv(self, request, collection_id):
        collection = self.get_object(request, collection_id)

        if not collection:
            self.message_user(request, "Collection not found", level="error")
            return HttpResponse(status=404)

        # Get all WixProducts associated with the collection
        wix_products = WixProduct.objects.filter(collections=collection)

        if not wix_products.exists():
            self.message_user(request, "No WixProducts found in this collection", level="warning")
            return HttpResponse(status=404)

        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{collection.title}_wix_products.csv"'

        # Define CSV headers
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

        # Write the product data to CSV
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

    # Add a custom button to export the CSV from the admin interface
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['export_button'] = format_html(
            '<a class="button" href="{}">Export Wix Products to CSV</a>',
            reverse('admin:export_wixproducts', args=[object_id])
        )
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    # Set the URL for the export action
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<int:collection_id>/export_wixproducts/', self.export_to_csv, name='export_wixproducts'),
        ]
        return custom_urls + urls

class VariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'price', 'get_options']
    search_fields = ['product__title', 'price']

    def get_options(self, obj):
        logger.debug(f"VariantAdmin: get_options for variant {obj.id}")
        return ", ".join([str(option) for option in obj.options.all()])

    get_options.short_description = 'Options'


class OptionValueInline(admin.TabularInline):
    model = OptionValue
    extra = 1
    fields = ['value']


class OptionCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    inlines = [OptionValueInline]


class WixProductAdmin(admin.ModelAdmin):
    list_display = [
        'handle_id', 'name', 'price', 'ribbon', 'inventory', 'visible', 'get_collections', 'created_at', 'updated_at'
    ]
    search_fields = ['name', 'handle_id', 'price', 'sku']
    list_filter = ['created_at', 'updated_at', 'collections', 'visible', 'inventory']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('handle_id', 'field_type', 'name', 'description', 'product_image_url', 'collections', 'sku', 'ribbon', 'price', 'surcharge', 'visible', 'inventory', 'discount_mode', 'discount_value', 'weight', 'cost')
        }),
        ('Product Options', {
            'fields': (
                ('product_option_name_1', 'product_option_type_1', 'product_option_description_1'),
                ('product_option_name_2', 'product_option_type_2', 'product_option_description_2'),
                ('product_option_name_3', 'product_option_type_3', 'product_option_description_3'),
                ('product_option_name_4', 'product_option_type_4', 'product_option_description_4'),
                ('product_option_name_5', 'product_option_type_5', 'product_option_description_5'),
                ('product_option_name_6', 'product_option_type_6', 'product_option_description_6'),
            )
        }),
        ('Additional Information', {
            'fields': (
                ('additional_info_title_1', 'additional_info_description_1'),
                ('additional_info_title_2', 'additional_info_description_2'),
                ('additional_info_title_3', 'additional_info_description_3'),
                ('additional_info_title_4', 'additional_info_description_4'),
                ('additional_info_title_5', 'additional_info_description_5'),
                ('additional_info_title_6', 'additional_info_description_6'),
            )
        }),
        ('Custom Text', {
            'fields': ('custom_text_field_1', 'custom_text_char_limit_1', 'custom_text_mandatory_1')
        }),
        ('Brand', {
            'fields': ('brand',)
        }),
    )

    def get_collections(self, obj):
        # Since it's ManyToMany, we loop through each collection and generate links
        collections = obj.collections.all()
        links = [format_html('<a href="{}">{}</a>', reverse('admin:agent_collection_change', args=[c.id]), c.title) for c in collections]
        return format_html(", ".join(links)) if links else "-"

    get_collections.short_description = 'Collections'


# Register models in the Django admin
admin.site.register(Collection, CollectionAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Variant, VariantAdmin)
admin.site.register(OptionCategory, OptionCategoryAdmin)
admin.site.register(WixProduct, WixProductAdmin)
