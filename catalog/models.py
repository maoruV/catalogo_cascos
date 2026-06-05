from django.db import models
from imagekit.models import ImageSpecField
from pilkit.processors import ResizeToFill


class Category(models.Model):
    """Product category taxonomy."""

    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Product(models.Model):
    """Catalog product."""

    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="products/", blank=True)
    active = models.BooleanField(default=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    # Thumbnail automático para las cards (800×600, crop centrado)
    thumbnail = ImageSpecField(
        source="image",
        processors=[ResizeToFill(800, 600)],
        format="WEBP",
        options={"quality": 82},
    )

    def __str__(self):
        return self.name
