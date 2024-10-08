import logging
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Collection, Product, Variant, Image, OptionCategory, OptionValue, WixProduct

logger = logging.getLogger(__name__)

class VariantInline(admin.TabularInline):
    model = Variant
    extra = 1
    fields = ['price', 'get_options', 'get_variant_images']
    readonly_fields = ['get_options', 'get_variant_images']

    def get_options(self, obj):
        logger.debug("VariantInline: get_options called")
        return ", ".join([str(option) for option in obj.options.all()])

    get_options.short_description = 'Options'

    def get_variant_images(self, obj):
        if obj.images.exists():
            images = obj.images.all()
            image_links = [format_html('<img src="{}" style="width: 50px; height: auto;">', image.url) for image in images]
            return format_html(" ".join(image_links))
        return "No images"
    
    get_variant_images.short_description = 'Images'

class ImageInline(admin.TabularInline):
    model = Image
    extra = 1
    fields = ['url', 'alt_text', 'get_image']
    readonly_fields = ['get_image']

    def get_image(self, obj):
        return format_html('<img src="{}" width="100" height="100" />', obj.url)

    get_image.short_description = 'Image Preview'


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
    list_display = ['pk', 'title', 'description', 'price', 'get_collections', 'allow_update', 'created_at', 'updated_at']
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


class CollectionAdmin(admin.ModelAdmin):
    list_display = ['pk', 'title', 'description', 'get_product_count', 'download_csv']
    search_fields = ['title', 'description']
    inlines = [ProductInlineInCollection, WixProductInline]  # Added WixProductInline here
    exclude = ('products',)

    def get_product_count(self, obj):
        return obj.products.count()

    get_product_count.short_description = 'Total Products'

    def download_csv(self, obj):
        if obj.csv_export:
            # Create a link to the CSV file for download
            return format_html('<a href="{}" download>Download CSV</a>', obj.csv_export.url)
        return "No CSV file"
    
    download_csv.short_description = 'CSV Export'

class VariantAdmin(admin.ModelAdmin):
    list_display = ['pk', 'product', 'price', 'get_options']
    search_fields = ['product__title', 'pk', 'price']

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
        'handle_id', 'name', 'field_type', 'price', 'ribbon', 'inventory', 'visible', 'get_collections', 
        'product_option_name_1', 'product_option_type_1', 'product_option_description_1',
        'created_at', 'updated_at'
    ]
    search_fields = ['name', 'handle_id', 'price', 'sku']
    list_filter = ['created_at', 'updated_at', 'field_type', 'collections', 'visible', 'inventory']
    
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

class ImageAdmin(admin.ModelAdmin):
    list_display = ['pk', 'product', 'url', 'alt_text']
    search_fields = ['product__title', 'pk', 'url', 'alt_text']
    list_filter = ['product']

# Register models in the Django admin
admin.site.register(Collection, CollectionAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Variant, VariantAdmin)
admin.site.register(OptionCategory, OptionCategoryAdmin)
admin.site.register(WixProduct, WixProductAdmin)
admin.site.register(Image, ImageAdmin)