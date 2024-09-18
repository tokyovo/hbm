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
        return f"{self.category.name}: {self.value}"


class Variant(models.Model):
    product = models.ForeignKey(Product, related_name="variants", on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    options = models.ManyToManyField(OptionValue, related_name="variants")  # Many-to-many to represent combinations of Size, Color, etc.

    def __str__(self):
        # Avoid recursion by accessing the `value` attribute of OptionValue directly
        option_str = ", ".join([option.value for option in self.options.all()])
        return f"{self.product.title} ({option_str}) - ${self.price}"


class Image(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    url = models.URLField()  # Store the image URL (from Shopify or your server)
    alt_text = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Image for {self.product.title}"
