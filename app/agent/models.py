from django.db import models


class Collection(models.Model):
    title = models.CharField(max_length=1024)
    description = models.TextField(blank=True, null=True)
    source_url = models.URLField(max_length=1024, unique=True)  # Increased length for the URL
    csv_export = models.FileField(upload_to='csv_exports/', blank=True, null=True)

    def __str__(self):
        return self.title


class Product(models.Model):
    title = models.CharField(max_length=1024)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    collections = models.ManyToManyField(Collection, related_name="products")  # Many-to-many relationship with collections
    source_url = models.URLField(max_length=1024, unique=True)  # Increased length for the URL
    allow_update = models.BooleanField(default=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class OptionCategory(models.Model):
    """
    Represents categories like "Size", "Color", etc.
    """
    name = models.CharField(max_length=521, unique=True)

    def __str__(self):
        return self.name


class OptionValue(models.Model):
    """
    Represents values like "Small", "Large" for Size, or "Red", "Blue" for Color.
    """
    category = models.ForeignKey(OptionCategory, related_name="values", on_delete=models.CASCADE)
    value = models.CharField(max_length=521)

    class Meta:
        unique_together = ('category', 'value')

    def __str__(self):
        return self.value

class Image(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    url = models.URLField(max_length=1024)  # Increased length for the URL
    alt_text = models.CharField(max_length=1024, blank=True, null=True)  # Increased length for alt_text

    def __str__(self):
        return f"Image for {self.product.title}"

class Variant(models.Model):
    product = models.ForeignKey(Product, related_name="variants", on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    options = models.ManyToManyField(OptionValue, related_name="variants")  # Many-to-many to represent combinations of Size, Color, etc.
    images = models.ManyToManyField('Image', related_name="variant_images", blank=True)

    def __str__(self):
        return f"Variant of {self.product.title}"

class WixProduct(models.Model):
    # Basic product fields
    handle_id = models.CharField(max_length=521)  # handleId
    field_type = models.CharField(max_length=521, default="Product")  # fieldType
    name = models.CharField(max_length=1024)  # Product name
    description = models.TextField(blank=True, null=True)  # Product description
    product_image_url = models.TextField(blank=True, null=True)  # Product image URL(s)
    collections = models.ManyToManyField(Collection, related_name="wix_products")  # Allow multiple collections
    sku = models.CharField(max_length=1024, blank=True, null=True)  # SKU
    ribbon = models.CharField(max_length=521, blank=True, null=True)  # Promotional label, like "sale"
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Product price
    surcharge = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Additional surcharge if any
    visible = models.BooleanField(default=True)  # Whether the product is visible
    discount_mode = models.CharField(max_length=521, blank=True, null=True)  # Discount mode
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Discount value
    inventory = models.CharField(max_length=521, default="InStock")  # Inventory status
    weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Product weight
    cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Product cost

    # Product Options (Up to 6)
    product_option_name_1 = models.CharField(max_length=1024, blank=True, null=True)  # productOptionName1
    product_option_type_1 = models.CharField(max_length=521, blank=True, null=True)  # productOptionType1 (e.g., COLOR or DROP_DOWN)
    product_option_description_1 = models.TextField(blank=True, null=True)  # productOptionDescription1
    
    product_option_name_2 = models.CharField(max_length=1024, blank=True, null=True)  # productOptionName2
    product_option_type_2 = models.CharField(max_length=521, blank=True, null=True)  # productOptionType2
    product_option_description_2 = models.TextField(blank=True, null=True)  # productOptionDescription2
    
    product_option_name_3 = models.CharField(max_length=1024, blank=True, null=True)  # productOptionName3
    product_option_type_3 = models.CharField(max_length=521, blank=True, null=True)  # productOptionType3
    product_option_description_3 = models.TextField(blank=True, null=True)  # productOptionDescription3
    
    product_option_name_4 = models.CharField(max_length=1024, blank=True, null=True)  # productOptionName4
    product_option_type_4 = models.CharField(max_length=521, blank=True, null=True)  # productOptionType4
    product_option_description_4 = models.TextField(blank=True, null=True)  # productOptionDescription4
    
    product_option_name_5 = models.CharField(max_length=1024, blank=True, null=True)  # productOptionName5
    product_option_type_5 = models.CharField(max_length=521, blank=True, null=True)  # productOptionType5
    product_option_description_5 = models.TextField(blank=True, null=True)  # productOptionDescription5
    
    product_option_name_6 = models.CharField(max_length=1024, blank=True, null=True)  # productOptionName6
    product_option_type_6 = models.CharField(max_length=521, blank=True, null=True)  # productOptionType6
    product_option_description_6 = models.TextField(blank=True, null=True)  # productOptionDescription6

    # Additional Info (Up to 6)
    additional_info_title_1 = models.CharField(max_length=1024, blank=True, null=True)  # additionalInfoTitle1
    additional_info_description_1 = models.TextField(blank=True, null=True)  # additionalInfoDescription1
    
    additional_info_title_2 = models.CharField(max_length=1024, blank=True, null=True)  # additionalInfoTitle2
    additional_info_description_2 = models.TextField(blank=True, null=True)  # additionalInfoDescription2
    
    additional_info_title_3 = models.CharField(max_length=1024, blank=True, null=True)  # additionalInfoTitle3
    additional_info_description_3 = models.TextField(blank=True, null=True)  # additionalInfoDescription3
    
    additional_info_title_4 = models.CharField(max_length=1024, blank=True, null=True)  # additionalInfoTitle4
    additional_info_description_4 = models.TextField(blank=True, null=True)  # additionalInfoDescription4
    
    additional_info_title_5 = models.CharField(max_length=1024, blank=True, null=True)  # additionalInfoTitle5
    additional_info_description_5 = models.TextField(blank=True, null=True)  # additionalInfoDescription5
    
    additional_info_title_6 = models.CharField(max_length=1024, blank=True, null=True)  # additionalInfoTitle6
    additional_info_description_6 = models.TextField(blank=True, null=True)  # additionalInfoDescription6

    # Custom Text Field
    custom_text_field_1 = models.TextField(blank=True, null=True)  # customTextField1
    custom_text_char_limit_1 = models.IntegerField(blank=True, null=True)  # customTextCharLimit1
    custom_text_mandatory_1 = models.BooleanField(default=False)  # customTextMandatory1

    # Branding
    brand = models.CharField(max_length=1024, blank=True, null=True)  # Product brand

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.handle_id}"
