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
    model = WixProduct
    extra = 0
    fields = ['handle_id', 'name', 'price', 'created_at', 'updated_at']
    readonly_fields = ['handle_id', 'name', 'price', 'created_at', 'updated_at']
    can_delete = False

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('collection')


class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'price', 'get_collections', 'created_at', 'updated_at']
    search_fields = ['title', 'description']
    list_filter = ['created_at', 'updated_at']
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
    list_display = ['title', 'description', 'get_product_count']
    search_fields = ['title', 'description']
    inlines = [ProductInlineInCollection, WixProductInline]  # Added WixProductInline here
    exclude = ('products',)

    def get_product_count(self, obj):
        return obj.products.count()

    get_product_count.short_description = 'Total Products'


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
    list_display = ['handle_id', 'name', 'price', 'get_collections', 'created_at', 'updated_at']
    search_fields = ['name', 'handle_id', 'price']
    list_filter = ['created_at', 'updated_at', 'collection']

    def get_collections(self, obj):
        collections = obj.collection.all()
        links = [format_html('<a href="{}">{}</a>', reverse('admin:agent_collection_change', args=[c.id]), c.title) for c in collections]
        return format_html(", ".join(links))

    get_collections.short_description = 'Collections'


# Register models in the Django admin
admin.site.register(Collection, CollectionAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Variant, VariantAdmin)
admin.site.register(OptionCategory, OptionCategoryAdmin)
admin.site.register(WixProduct, WixProductAdmin)
