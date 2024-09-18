from django.contrib import admin
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
        """Display the collections a product belongs to in list view."""
        return ", ".join([c.title for c in obj.collections.all()])
    get_collections.short_description = 'Collections'


class CollectionAdmin(admin.ModelAdmin):
    """
    Custom admin interface for Collections.
    """
    list_display = ['title', 'description']
    search_fields = ['title', 'description']
    inlines = [ProductInline]

    exclude = ('products',)  # Hide the 'products' many-to-many field


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

