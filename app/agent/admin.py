from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Collection, Product, Variant, Image, OptionCategory, OptionValue


class VariantInline(admin.TabularInline):
    model = Variant
    extra = 1
    fields = ['title', 'price']


class ImageInline(admin.TabularInline):
    model = Image
    extra = 1
    fields = ['url', 'alt_text']


class ProductInlineInCollection(admin.TabularInline):
    """
    Inline for showing products in Collection admin.
    """
    model = Product.collections.through  # Many-to-many relationship for collections
    extra = 0
    fields = ['get_product_link']

    readonly_fields = ['get_product_link']  # Make the field read-only

    def get_product_link(self, obj):
        """
        Return a clickable link to the product admin page.
        """
        product = obj.product
        url = reverse('admin:agent_product_change', args=[product.id])  # Use reverse to dynamically generate the URL
        return format_html('<a href="{}">{}</a>', url, product.title)

    get_product_link.short_description = 'Product'


class ProductAdmin(admin.ModelAdmin):
    """
    Custom admin interface for Products.
    """
    list_display = ['title', 'description', 'get_collections', 'created_at', 'updated_at']
    search_fields = ['title', 'description']
    list_filter = ['created_at', 'updated_at']
    inlines = [VariantInline, ImageInline]

    def get_collections(self, obj):
        collections = obj.collections.all()
        links = [format_html('<a href="{}">{}</a>', self.get_admin_url(c), c.title) for c in collections]
        return format_html(", ".join(links))

    get_collections.short_description = 'Collections'

    def get_admin_url(self, obj):
        url = reverse('admin:agent_collection_change', args=[obj.id])
        return url


class CollectionAdmin(admin.ModelAdmin):
    """
    Custom admin interface for Collections.
    """
    list_display = ['title', 'description', 'get_product_count']
    search_fields = ['title', 'description']
    inlines = [ProductInlineInCollection]

    exclude = ('products',)

    def get_product_count(self, obj):
        return obj.products.count()

    get_product_count.short_description = 'Total Products'


class OptionValueInline(admin.TabularInline):
    model = OptionValue
    extra = 1
    fields = ['value']


class OptionCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    inlines = [OptionValueInline]


# Register models in the Django admin
admin.site.register(Collection, CollectionAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(OptionCategory, OptionCategoryAdmin)
