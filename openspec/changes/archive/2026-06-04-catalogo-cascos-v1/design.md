# Design: Catálogo de Cascos y Accesorios — v1

## Technical Approach

Single `catalog` Django app with class-based views, HTMX GET-based filtering, and Django Paginator. All filtering, search, and pagination reuse the same ListView via query params and return HTML partials for HTMX swaps. Admin provides full CRUD for both models. Pillow + local `MEDIA_ROOT` handles images. Strict TDD: tests drive every model, view, admin registration, and HTMX interaction.

## Architecture Decisions

### Decision: Models — Product and Category

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Product fields inline vs abstract base | No reuse opportunity yet; inline is simpler | Inline on Product |
| `on_delete=CASCADE` vs `SET_NULL` | CASCADE loses product data if category deleted | **SET_NULL** (specs require products preserved) |

- **Category**: `id` (auto), `name` (CharField 100, unique, `__str__` → name)
- **Product**: `id`, `name` (200), `brand` (100), `price` (Decimal 10/2), `description` (TextField, blank), `image` (ImageField, upload_to='products/', blank), `active` (Boolean, default=True), `category` (FK→Category, null, blank, `on_delete=SET_NULL`)

### Decision: Views — ListView as single entry point for both full page and HTMX partials

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Separate views for page vs partial | Duplicate filter logic | **Single `ProductListView`** — `HX-Request` header switches template (`_list.html` vs `_partial_products.html`) |
| Separate search view | Same queryset logic repeated | **Same view** — `q` param filtered via `name__icontains` |
| Function views vs CBV | Project uses CBV convention | **CBV**: `ProductListView(ListView)`, `ProductDetailView(DetailView)` |

The view applies filters in order: `active=True` → `q` → `categoria` → `marca` → `precio_min/precio_max`. Malformed numeric params are silently ignored per spec.

### Decision: URLs

| Pattern | View | Name |
|---------|------|------|
| `/` | `ProductListView` | `catalog:product_list` |
| `/<pk>/` | `ProductDetailView` | `catalog:product_detail` |

Included under `catalog/urls.py` with `app_name='catalog'`. Root `config/urls.py` includes `path('', include('catalog.urls'))` and adds `static(settings.MEDIA_URL, ...)` for dev media serving.

### Decision: Templates

```
catalog/templates/catalog/
├── pages/
│   ├── product_list.html        # Full page extends base, includes partial
│   └── product_detail.html      # Full detail page
├── partials/
│   ├── _product_grid.html       # Product cards grid (HTMX-swappable)
│   ├── _product_card.html       # Single card (included by _product_grid)
│   ├── _filters.html            # Category/marca/price filter form
│   ├── _search_bar.html         # Search input with hx-get + hx-trigger
│   └── _pagination.html         # Page number links with hx-get
└── base.html                    # Base layout, HTMX from CDN
```

`product_list.html` includes `_search_bar`, `_filters`, `_product_grid`, `_pagination`. HTMX requests target `#product-grid` and `#pagination` using `hx-target`.

### Decision: Admin

| Model | Admin options |
|-------|---------------|
| Category | `list_display = ('name', 'product_count')`, `search_fields = ('name',)` |
| Product | `list_display = ('name', 'brand', 'price', 'active', 'category')`, `list_filter = ('active', 'category')`, `search_fields = ('name', 'brand')` |

`product_count` is a method using `self.product_set.count()` for the Category admin.

### Decision: HTMX + Pagination Integration

HTMX swaps the grid and pagination together. Each pagination link carries current filter params via `hx-get="?page=2&categoria=..."`. The `hx-trigger` on search uses `keyup delay:300ms`. `hx-target="#product-grid"` swaps the grid; pagination controls are swapped via a second target or re-rendered inside the same partial.

## Data Flow

```
User Browser                  Django Server
    │                              │
    ├── GET /                      → ProductListView → filter(active=True)
    │                              ← product_list.html (full page)
    │                              │
    ├── type in search bar         │
    │   hx-get="/?q=casco"         → ProductListView → filter(q, active)
    │   hx-target="#product-grid"  ← _product_grid.html partial
    │                              │
    ├── click "page 2"             │
    │   hx-get="/?page=2&q=casco"  → ProductListView → Paginator page 2
    │   hx-target="#product-grid"  ← _product_grid.html + _pagination
    │                              │
    ├── click product card         │
    │   GET /<pk>/                 → ProductDetailView → get_object()
    │                              ← product_detail.html
    │                              │
    ├── GET /media/products/*.jpg  → static() dev handler → file response
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `catalog/__init__.py` | Create | App package init |
| `catalog/models.py` | Create | Product and Category models |
| `catalog/admin.py` | Create | ModelAdmin registration for both |
| `catalog/views.py` | Create | ProductListView, ProductDetailView |
| `catalog/urls.py` | Create | URL patterns for catalog |
| `catalog/templates/catalog/base.html` | Create | Base layout + HTMX CDN script |
| `catalog/templates/catalog/pages/product_list.html` | Create | Full list page |
| `catalog/templates/catalog/pages/product_detail.html` | Create | Detail page |
| `catalog/templates/catalog/partials/_product_grid.html` | Create | Grid partial for HTMX swap |
| `catalog/templates/catalog/partials/_product_card.html` | Create | Single product card |
| `catalog/templates/catalog/partials/_filters.html` | Create | Filter form partial |
| `catalog/templates/catalog/partials/_search_bar.html` | Create | Search input with HTMX attrs |
| `catalog/templates/catalog/partials/_pagination.html` | Create | Paginator links partial |
| `catalog/tests.py` | Create | All unit/integration tests |
| `config/settings.py` | Modify | Add `catalog` to INSTALLED_APPS, add MEDIA_URL/MEDIA_ROOT |
| `config/urls.py` | Modify | Include catalog URLs, add media serving in DEBUG |
| `pyproject.toml` | Modify | Add `Pillow>=11` to dependencies |

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | Model fields, constraints, `__str__`, `on_delete` behavior | Django TestCase — create instances, assert field values, assert uniqueness error, assert SET_NULL on delete |
| Integration | ListView filtering (each param), pagination, detail view (active=200, inactive=404) | Django TestCase — GET with query params, assert response context count, assert template used |
| Integration | Admin CRUD registration | `AdminSite` + `ModelAdmin` instance checks, `list_display` values |
| Integration | HTMX partial responses | GET with `HTTP_HX_REQUEST='true'` header, assert partial template rendered, no `<html>` wrapper |
| Integration | Media serving (DEBUG) | `static()` in urls, assert dev media URL resolution |
| Integration | ImageField upload | Use `SimpleUploadedFile` with a small test image, assert file saved and URL resolvable |
| Edge | Malformed price params, empty brand, non-existent category, missing image | Assert filter silently skipped, 200 returned, empty state message shown |
| Edge | Paginator edge cases (page out of range, last page partial) | Assert 200 with empty page, or page clamped |

## Migration

Fresh project with no prior migrations. Plan:

1. `python manage.py makemigrations catalog` — creates 001_initial with both models
2. `python manage.py migrate` — applies to SQLite
3. No data migration needed (greenfield)
4. Rollback: `python manage.py migrate catalog zero` removes all catalog tables
