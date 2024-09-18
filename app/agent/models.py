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


class Variant(models.Model):
    product = models.ForeignKey(Product, related_name="variants", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)  # E.g., "Red / Small" or "Blue / Large"
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.title} - {self.title}"


class Image(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    url = models.URLField()  # Store the image URL (from Shopify or your server)
    alt_text = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Image for {self.product.title}"
