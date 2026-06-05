"""Views for the catalog app."""

from django.db.models import Q
from django.views.generic import DetailView, ListView

from catalog.models import Category, Product


class ProductListView(ListView):
    """List active products with filtering, search, and pagination.

    Supports GET params: q, categoria, precio_min, precio_max.
    Uses ``HX-Request`` header to switch between full page and HTMX partial.
    """

    model = Product
    paginate_by = 6
    ordering = ["name"]

    def get_template_names(self):
        if self.request.headers.get("HX-Request") == "true":
            return ["catalog/partials/_product_grid.html"]
        return ["catalog/pages/product_list.html"]

    def get_queryset(self):
        qs = super().get_queryset().filter(active=True)

        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(name__icontains=q) | Q(brand__icontains=q)
            )

        categoria = self.request.GET.get("categoria", "").strip()
        if categoria:
            qs = qs.filter(category_id=categoria)

        precio_min = self.request.GET.get("precio_min", "").strip()
        if precio_min:
            try:
                qs = qs.filter(price__gte=float(precio_min))
            except (ValueError, TypeError):
                pass

        precio_max = self.request.GET.get("precio_max", "").strip()
        if precio_max:
            try:
                qs = qs.filter(price__lte=float(precio_max))
            except (ValueError, TypeError):
                pass

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Preserve filter values for form state
        for param in ("q", "categoria", "precio_min", "precio_max"):
            context[param] = self.request.GET.get(param, "")
        # All categories for the filter dropdown
        context["categories"] = Category.objects.all()
        return context


class ProductDetailView(DetailView):
    """Display a single active product. Inactive products return 404."""

    model = Product
    template_name = "catalog/pages/product_detail.html"

    def get_queryset(self):
        return super().get_queryset().filter(active=True)
