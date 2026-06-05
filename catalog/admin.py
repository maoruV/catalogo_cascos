from django.contrib import admin

from catalog.models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "product_count")
    search_fields = ("name",)

    @staticmethod
    def product_count(obj):
        """Return the number of products in this category."""
        return obj.product_set.count()


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "price", "active", "category")
    list_filter = ("active", "category")
    search_fields = ("name", "brand")
