from django.db import models


class Collection(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    source_url = models.URLField(unique=True)  # Stores the URL from which the collection was parsed

    def __str__(self):
        return self.title


class Product(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    collections = models.ManyToManyField(Collection, related_name="products")  # Many-to-many relationship with collections
    source_url = models.URLField(unique=True)  # Stores the URL from which the product was parsed
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class OptionCategory(models.Model):
    """
    Represents categories like "Size", "Color", etc.
    """
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class OptionValue(models.Model):
    """
    Represents values like "Small", "Large" for Size, or "Red", "Blue" for Color.
    """
    category = models.ForeignKey(OptionCategory, related_name="values", on_delete=models.CASCADE)
    value = models.CharField(max_length=50)

    class Meta:
        unique_together = ('category', 'value')

    def __str__(self):
        return self.value


class Variant(models.Model):
    product = models.ForeignKey(Product, related_name="variants", on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    options = models.ManyToManyField(OptionValue, related_name="variants")  # Many-to-many to represent combinations of Size, Color, etc.

    def __str__(self):
        return f"Variant of {self.product.title}"


class Image(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    url = models.URLField()  # Store the image URL (from Shopify or your server)
    alt_text = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Image for {self.product.title}"

class WixProduct(models.Model):
    handle_id = models.CharField(max_length=50, unique=True)  # Corresponds to 'handleId' in the CSV
    field_type = models.CharField(max_length=50, default="Product")  # Product or Variant
    name = models.CharField(max_length=255)  # Product name
    description = models.TextField(blank=True, null=True)  # Product description
    product_image_url = models.TextField(blank=True, null=True)  # Multiple images separated by semicolons
    collection = models.ForeignKey(Collection, related_name="wix_products", on_delete=models.CASCADE)  # ForeignKey to Collection model
    sku = models.CharField(max_length=50, blank=True, null=True)  # Product SKU
    ribbon = models.CharField(max_length=50, blank=True, null=True)  # Product label (sale, new, etc.)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Product price
    surcharge = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Additional surcharge if any
    additional_info_title_1 = models.CharField(max_length=255, blank=True, null=True)  # Additional info title 1
    additional_info_description_1 = models.TextField(blank=True, null=True)  # Additional info description 1
    additional_info_title_2 = models.CharField(max_length=255, blank=True, null=True)  # Additional info title 2
    additional_info_description_2 = models.TextField(blank=True, null=True)  # Additional info description 2
    additional_info_title_3 = models.CharField(max_length=255, blank=True, null=True)  # Additional info title 3
    additional_info_description_3 = models.TextField(blank=True, null=True)  # Additional info description 3
    additional_info_title_4 = models.CharField(max_length=255, blank=True, null=True)  # Additional info title 4
    additional_info_description_4 = models.TextField(blank=True, null=True)  # Additional info description 4
    additional_info_title_5 = models.CharField(max_length=255, blank=True, null=True)  # Additional info title 5
    additional_info_description_5 = models.TextField(blank=True, null=True)  # Additional info description 5
    additional_info_title_6 = models.CharField(max_length=255, blank=True, null=True)  # Additional info title 6
    additional_info_description_6 = models.TextField(blank=True, null=True)  # Additional info description 6
    custom_text_field_1 = models.TextField(blank=True, null=True)  # Custom text field 1 (for engravings, etc.)
    custom_text_char_limit_1 = models.IntegerField(blank=True, null=True)  # Character limit for custom text
    custom_text_mandatory_1 = models.BooleanField(default=False)  # Whether custom text is mandatory
    brand = models.CharField(max_length=100, blank=True, null=True)  # Product brand
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically sets the date when the product is created
    updated_at = models.DateTimeField(auto_now=True)  # Automatically updates whenever the product is updated

    def __str__(self):
        return f"{self.name} - {self.handle_id}"
