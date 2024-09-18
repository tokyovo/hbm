from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse  # Import for dynamic URL reversal
from .models import Collection, Product, Variant, Image, OptionCategory, OptionValue


class VariantInline(admin.TabularInline):
    model = Variant
    extra = 1
    fields = ['title', 'price']  # Display only title and price in the inline


class ImageInline(admin.TabularInline):
    model = Image
    extra = 1
    fields = ['url', 'alt_text']  # Display image URL and alt text in the inline


class ProductInline(admin.TabularInline):
    model = Product.collections.through  # Many-to-many relationship for collections
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    """
    Custom admin interface for Products.
    """
    list_display = ['title', 'description', 'get_collections', 'created_at', 'updated_at']
    search_fields = ['title', 'description']
    list_filter = ['created_at', 'updated_at']
    inlines = [VariantInline, ImageInline]

    def get_collections(self, obj):
        """Display the collections a product belongs to with links to the collection in admin."""
        collections = obj.collections.all()
        links = [format_html('<a href="{}">{}</a>', self.get_admin_url(c), c.title) for c in collections]
        return format_html(", ".join(links))  # Ensure the HTML is rendered correctly

    get_collections.short_description = 'Collections'

    def get_admin_url(self, obj):
        """Return the admin URL for the related collection object dynamically."""
        url = reverse('admin:agent_collection_change', args=[obj.id])  # Dynamically generate URL
        return url


class CollectionAdmin(admin.ModelAdmin):
    """
    Custom admin interface for Collections.
    """
    list_display = ['title', 'description', 'get_product_count']  # Add product count to list display
    search_fields = ['title', 'description']
    inlines = [ProductInline]

    exclude = ('products',)  # Hide the 'products' many-to-many field

    def get_product_count(self, obj):
        """Return the total number of products in a collection."""
        return obj.products.count()  # Count the number of related products
    get_product_count.short_description = 'Total Products'  # Set the column name in the admin


class OptionValueInline(admin.TabularInline):
    """
    Inline for Option Values (e.g., Small, Large).
    """
    model = OptionValue
    extra = 1
    fields = ['value']


class OptionCategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for Option Categories (e.g., Size, Color).
    """
    list_display = ['name']
    search_fields = ['name']
    inlines = [OptionValueInline]


# Register models in the Django admin
admin.site.register(Collection, CollectionAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(OptionCategory, OptionCategoryAdmin)
