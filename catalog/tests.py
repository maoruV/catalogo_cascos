"""Tests for the catalog app."""

from decimal import Decimal

from django.contrib.admin import AdminSite
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from catalog.admin import CategoryAdmin, ProductAdmin
from catalog.models import Category, Product


class CategoryModelTests(TestCase):
    """Tests for the Category model."""

    def test_create_category_sets_name(self):
        """Creating a Category should store the name."""
        category = Category.objects.create(name="Casco Integral")
        self.assertEqual(category.name, "Casco Integral")

    def test_category_str_returns_name(self):
        """Category.__str__() should return the category name."""
        category = Category.objects.create(name="Casco Integral")
        self.assertEqual(str(category), "Casco Integral")

    def test_duplicate_category_name_raises_integrity_error(self):
        """Creating two categories with the same name should raise IntegrityError."""
        Category.objects.create(name="Casco Integral")
        with self.assertRaises(IntegrityError):
            Category.objects.create(name="Casco Integral")


class ProductModelTests(TestCase):
    """Tests for the Product model."""

    def setUp(self):
        self.category = Category.objects.create(name="Casco Integral")

    def test_create_product_with_all_fields(self):
        """Creating a Product with all fields should store them correctly."""
        product = Product.objects.create(
            name="Helmet Pro X",
            brand="BrandA",
            price=199.99,
            description="A full-face racing helmet",
            active=True,
            category=self.category,
        )
        self.assertEqual(product.name, "Helmet Pro X")
        self.assertEqual(product.brand, "BrandA")
        self.assertEqual(product.price, 199.99)
        self.assertEqual(product.description, "A full-face racing helmet")
        self.assertTrue(product.active)
        self.assertEqual(product.category, self.category)

    def test_create_product_minimal_fields(self):
        """Creating a Product with only required fields should use defaults."""
        product = Product.objects.create(
            name="Basic Helmet",
            brand="BrandB",
            price=49.99,
        )
        self.assertEqual(product.name, "Basic Helmet")
        self.assertEqual(product.brand, "BrandB")
        self.assertEqual(product.price, 49.99)
        # Optional fields should be blank/default
        self.assertEqual(product.description, "")
        self.assertTrue(product.active)
        self.assertIsNone(product.category)
        self.assertEqual(product.image, "")

    def test_product_str_returns_name(self):
        """Product.__str__() should return the product name."""
        product = Product.objects.create(
            name="Helmet Pro X",
            brand="BrandA",
            price=199.99,
        )
        self.assertEqual(str(product), "Helmet Pro X")

    def test_product_linked_to_category(self):
        """A Product linked to a Category should return the correct Category."""
        product = Product.objects.create(
            name="Gloves",
            brand="BrandC",
            price=29.99,
            category=self.category,
        )
        self.assertEqual(product.category, self.category)
        self.assertEqual(product.category.name, "Casco Integral")

    def test_category_delete_sets_product_category_null(self):
        """Deleting a Category should set related Product category to NULL (SET_NULL)."""
        product = Product.objects.create(
            name="Helmet Pro X",
            brand="BrandA",
            price=199.99,
            category=self.category,
        )
        self.category.delete()
        product.refresh_from_db()
        self.assertIsNone(product.category)

    def test_product_defaults_active_true(self):
        """A Product created without active field should default to True."""
        product = Product.objects.create(
            name="Default Active",
            brand="BrandD",
            price=50.00,
        )
        self.assertTrue(product.active)

    def test_product_inactive_false(self):
        """A Product created with active=False should store False."""
        product = Product.objects.create(
            name="Inactive Item",
            brand="BrandE",
            price=10.00,
            active=False,
        )
        self.assertFalse(product.active)

    def test_product_category_is_optional(self):
        """A Product should be creatable without a category."""
        product = Product.objects.create(
            name="No Category",
            brand="BrandF",
            price=25.00,
        )
        self.assertIsNone(product.category)


class CategoryAdminTests(TestCase):
    """Tests for the Category admin registration."""

    def setUp(self):
        self.site = AdminSite()
        self.model_admin = CategoryAdmin(Category, self.site)

    def test_category_admin_list_display(self):
        """CategoryAdmin should have the correct list_display."""
        expected = ("name", "product_count")
        self.assertEqual(self.model_admin.list_display, expected)

    def test_category_admin_search_fields(self):
        """CategoryAdmin should have search_fields containing 'name'."""
        self.assertIn("name", self.model_admin.search_fields)

    def test_product_count_method_exists(self):
        """CategoryAdmin should have a product_count method."""
        self.assertTrue(hasattr(self.model_admin, "product_count"))

    def test_product_count_returns_zero_for_empty_category(self):
        """product_count should return 0 for a category with no products."""
        category = Category.objects.create(name="Empty Category")
        self.assertEqual(self.model_admin.product_count(category), 0)


class ProductAdminTests(TestCase):
    """Tests for the Product admin registration."""

    def setUp(self):
        self.site = AdminSite()
        self.model_admin = ProductAdmin(Product, self.site)
        self.category = Category.objects.create(name="Casco Integral")

    def test_product_admin_list_display(self):
        """ProductAdmin should have the correct list_display."""
        expected = ("name", "brand", "price", "active", "category")
        self.assertEqual(self.model_admin.list_display, expected)

    def test_product_admin_list_filter(self):
        """ProductAdmin should have list_filter containing 'active' and 'category'."""
        self.assertIn("active", self.model_admin.list_filter)
        self.assertIn("category", self.model_admin.list_filter)

    def test_product_admin_search_fields(self):
        """ProductAdmin should have search_fields containing 'name' and 'brand'."""
        self.assertIn("name", self.model_admin.search_fields)
        self.assertIn("brand", self.model_admin.search_fields)


class ProductListViewTests(TestCase):
    """Tests for ProductListView — filtering, pagination, HTMX detection."""

    @classmethod
    def setUpTestData(cls):
        cls.category_a = Category.objects.create(name="Integral")
        cls.category_b = Category.objects.create(name="Modular")
        products_data = [
            ("Casco Integral A", "Shark", 100.00, cls.category_a, True),
            ("Casco Integral B", "Shark", 200.00, cls.category_a, True),
            ("Casco Modular A", "AGV", 300.00, cls.category_b, True),
            ("Casco Modular B", "AGV", 400.00, cls.category_b, True),
            ("Inactive Product", "BrandX", 50.00, None, False),
        ]
        for name, brand, price, cat, active in products_data:
            Product.objects.create(
                name=name, brand=brand, price=price,
                category=cat, active=active,
            )

    def test_list_returns_only_active_products(self):
        """GET / should return only active products."""
        response = self.client.get(reverse("catalog:product_list"))
        self.assertEqual(response.status_code, 200)
        names = [p.name for p in response.context["product_list"]]
        self.assertIn("Casco Integral A", names)
        self.assertIn("Casco Modular B", names)
        self.assertNotIn("Inactive Product", names)

    def test_list_paginated_by_six(self):
        """List view should paginate at 6 products per page."""
        # Create 10 more active products to reach 14 total active
        for i in range(10):
            Product.objects.create(
                name=f"Extra Product {i}", brand="BrandY",
                price=Decimal("99.99"), active=True,
            )
        response = self.client.get(reverse("catalog:product_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["product_list"]), 6)
        self.assertTrue(response.context["is_paginated"])

    def test_list_shows_empty_state_when_no_active_products(self):
        """Empty active products should show a no-products message."""
        Product.objects.all().delete()
        response = self.client.get(reverse("catalog:product_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No se encontraron productos")
        self.assertEqual(len(response.context["product_list"]), 0)

    # --- q (text search) ---

    def test_search_q_filters_by_name_icontains(self):
        """GET ?q=Casco should return only products whose name contains 'Casco'."""
        response = self.client.get(reverse("catalog:product_list"), {"q": "Casco"})
        self.assertEqual(response.status_code, 200)
        names = [p.name for p in response.context["product_list"]]
        self.assertIn("Casco Integral A", names)
        self.assertIn("Casco Modular B", names)
        # Inactive product should not appear even if name matches
        self.assertNotIn("Inactive Product", names)

    def test_search_q_no_matches_shows_empty(self):
        """GET ?q=Zapatillas with no matches should show empty state."""
        response = self.client.get(reverse("catalog:product_list"), {"q": "Zapatillas"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["product_list"]), 0)
        self.assertContains(response, "No se encontraron productos")

    def test_search_q_with_htmx_header_returns_partial(self):
        """Request with HX-Request header should use the grid partial template."""
        response = self.client.get(
            reverse("catalog:product_list"), {"q": "Integral"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        # Should NOT render the full page (no <html> or <body> tags)
        self.assertNotContains(response, "<html")
        self.assertNotContains(response, "<body")

    # --- categoria (category filter) ---

    def test_filter_categoria_by_id(self):
        """GET ?categoria=1 should return only products in that category."""
        response = self.client.get(
            reverse("catalog:product_list"),
            {"categoria": self.category_a.pk},
        )
        self.assertEqual(response.status_code, 200)
        names = [p.name for p in response.context["product_list"]]
        self.assertIn("Casco Integral A", names)
        self.assertNotIn("Casco Modular A", names)

    def test_filter_categoria_nonexistent_returns_empty(self):
        """GET ?categoria=999 with no matching category should show empty state."""
        response = self.client.get(
            reverse("catalog:product_list"), {"categoria": 999},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["product_list"]), 0)
        self.assertContains(response, "No se encontraron productos")

    # --- q search by brand ---

    def test_search_q_finds_by_brand(self):
        """GET ?q=shark should match products whose brand contains 'shark'."""
        response = self.client.get(
            reverse("catalog:product_list"), {"q": "shark"},
        )
        self.assertEqual(response.status_code, 200)
        names = [p.name for p in response.context["product_list"]]
        self.assertIn("Casco Integral A", names)
        self.assertIn("Casco Integral B", names)
        self.assertNotIn("Casco Modular A", names)

    # --- precio_min / precio_max ---

    def test_filter_price_range_inclusive(self):
        """GET ?precio_min=150&precio_max=350 should return products 200 and 300."""
        response = self.client.get(reverse("catalog:product_list"), {
            "precio_min": 150, "precio_max": 350,
        })
        self.assertEqual(response.status_code, 200)
        prices = [p.price for p in response.context["product_list"]]
        self.assertIn(Decimal("200.00"), prices)
        self.assertIn(Decimal("300.00"), prices)
        self.assertNotIn(Decimal("100.00"), prices)
        self.assertNotIn(Decimal("400.00"), prices)

    def test_filter_price_min_only(self):
        """GET ?precio_min=250 should return products >= 250."""
        response = self.client.get(
            reverse("catalog:product_list"), {"precio_min": 250},
        )
        self.assertEqual(response.status_code, 200)
        prices = [p.price for p in response.context["product_list"]]
        self.assertIn(Decimal("300.00"), prices)
        self.assertIn(Decimal("400.00"), prices)
        self.assertNotIn(Decimal("100.00"), prices)

    def test_filter_price_max_only(self):
        """GET ?precio_max=250 should return products <= 250."""
        response = self.client.get(
            reverse("catalog:product_list"), {"precio_max": 250},
        )
        self.assertEqual(response.status_code, 200)
        prices = [p.price for p in response.context["product_list"]]
        self.assertIn(Decimal("100.00"), prices)
        self.assertIn(Decimal("200.00"), prices)
        self.assertNotIn(Decimal("300.00"), prices)

    def test_filter_malformed_price_silently_ignored(self):
        """GET ?precio_min=abc should be silently ignored."""
        response = self.client.get(
            reverse("catalog:product_list"), {"precio_min": "abc"},
        )
        self.assertEqual(response.status_code, 200)
        # All active products returned
        self.assertEqual(len(response.context["product_list"]), 4)

    # --- Template switching ---

    def test_htmx_request_uses_partial_template(self):
        """Request with HX-Request header should render partial template."""
        response = self.client.get(
            reverse("catalog:product_list"),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/partials/_product_grid.html")

    def test_full_page_request_uses_list_template(self):
        """Normal request should render the full list page template."""
        response = self.client.get(reverse("catalog:product_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/pages/product_list.html")

    # --- Task 5.1: HTMX partial response test ---

    def test_htmx_partial_has_no_html_wrapper(self):
        """HTMX request should return partial with no <html> or <body> tags."""
        response = self.client.get(
            reverse("catalog:product_list"),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/partials/_product_grid.html")
        self.assertNotContains(response, "<html")
        self.assertNotContains(response, "<body")

    # --- Task 5.2: Edge case tests ---

    def test_search_q_empty_returns_all_active(self):
        """GET ?q= (empty) should return all active products."""
        response = self.client.get(
            reverse("catalog:product_list"), {"q": ""},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["product_list"]), 4)

    def test_missing_image_in_list_renders_fallback(self):
        """Product without image in list should render with placeholder, no crash."""
        Product.objects.create(
            name="No Image Product", brand="BrandX",
            price=10.00, active=True,
        )
        response = self.client.get(reverse("catalog:product_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No Image Product")


class ProductImageTests(TestCase):
    """Tests for image upload, media serving, and missing image handling."""

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Integral")

    # --- Task 5.3: Image upload + media serving tests ---

    def test_product_with_uploaded_image_saves_and_resolves_url(self):
        """Product with SimpleUploadedFile image should save and return a URL."""
        image_content = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00'
            b'\x80\x00\x00\xff\xff\xff\x00\x00\x00'
            b'\x21\xf9\x04\x00\x00\x00\x00\x00'
            b'\x2c\x00\x00\x00\x00\x01\x00\x01\x00'
            b'\x00\x02\x02\x44\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            "test.gif", image_content, content_type="image/gif",
        )
        product = Product.objects.create(
            name="Helmet With Image", brand="Shark", price=199.99,
            image=uploaded, active=True, category=self.category,
        )
        self.assertTrue(product.image)
        self.assertTrue(product.image.url)
        self.assertIn("/media/products/", product.image.url)
        self.assertTrue(product.image.url.endswith(".gif"))

    def test_product_blank_image_renders_detail_without_error(self):
        """Product with blank image should render detail page with placeholder."""
        product = Product.objects.create(
            name="No Pic Helmet", brand="BrandX", price=50.00,
            active=True, category=self.category,
        )
        response = self.client.get(
            reverse("catalog:product_detail", kwargs={"pk": product.pk}),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No Pic Helmet")
        self.assertNotContains(response, "Broken")

    def test_product_blank_image_in_list_renders_without_error(self):
        """Product with blank image should render in list without error."""
        Product.objects.create(
            name="List No Pic", brand="BrandX", price=25.00,
            active=True, category=self.category,
        )
        response = self.client.get(reverse("catalog:product_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "List No Pic")


class ProductDetailViewTests(TestCase):
    """Tests for ProductDetailView."""

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Integral")
        cls.active_product = Product.objects.create(
            name="Active Helmet", brand="Shark", price=199.99,
            category=cls.category, active=True,
        )
        cls.inactive_product = Product.objects.create(
            name="Inactive Helmet", brand="BrandX", price=99.99,
            active=False,
        )

    def test_active_product_returns_200(self):
        """GET /<active_pk>/ should return 200 with product details."""
        response = self.client.get(
            reverse("catalog:product_detail", kwargs={"pk": self.active_product.pk}),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Active Helmet")
        self.assertContains(response, "Shark")
        self.assertContains(response, "$ 200")

    def test_inactive_product_returns_404(self):
        """GET /<inactive_pk>/ should return 404."""
        response = self.client.get(
            reverse("catalog:product_detail", kwargs={"pk": self.inactive_product.pk}),
        )
        self.assertEqual(response.status_code, 404)

    def test_nonexistent_product_returns_404(self):
        """GET /<nonexistent_pk>/ should return 404."""
        response = self.client.get(
            reverse("catalog:product_detail", kwargs={"pk": 99999}),
        )
        self.assertEqual(response.status_code, 404)
