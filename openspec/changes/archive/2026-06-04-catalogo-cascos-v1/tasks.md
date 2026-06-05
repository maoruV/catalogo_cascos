# Tasks: Catálogo de Cascos y Accesorios — v1

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~529 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1: Foundation → PR 2: Views+Templates → PR 3: Tests |
| Delivery strategy | ask-always |
| Chain strategy | pending |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Base |
|------|------|-----------|------|
| 1 | App scaffold, models, admin, Pillow, media config, migrations | PR 1 | feature/catalogo-cascos-v1 |
| 2 | Views, URLs, 7 templates | PR 2 | PR 1 branch |
| 3 | Full test suite (HTMX, edge cases, images, media) | PR 3 | PR 2 branch |

## Phase 1: Foundation (TDD)

- [x] 1.1 [RED] Write Category + Product model tests (fields, `__str__`, unique, SET_NULL) — `catalog/tests.py`
- [x] 1.2 [GREEN] Create Category + Product models — `catalog/models.py`
- [x] 1.3 Add Pillow to deps — `pyproject.toml` via `uv add pillow`
- [x] 1.4 Configure `catalog` in INSTALLED_APPS, MEDIA_URL/MEDIA_ROOT — `config/settings.py`
- [x] 1.5 Run `makemigrations catalog` + `migrate`

## Phase 2: Admin

- [x] 2.1 [RED] Write admin registration tests (list_display, search_fields, product_count) — `catalog/tests.py`
- [x] 2.2 [GREEN] Create admin.py with ModelAdmin for Category + Product — `catalog/admin.py`

## Phase 3: Core Views + URLs

- [x] 3.1 [RED] Write ProductListView tests (filters, pagination, HTMX partial header detection) — `catalog/tests.py`
- [x] 3.2 [RED] Write ProductDetailView tests (active=200, inactive=404) — `catalog/tests.py`
- [x] 3.3 [GREEN] Create views.py with ProductListView + ProductDetailView — `catalog/views.py`
- [x] 3.4 Create urls.py (`app_name='catalog'`, `/` and `/<pk>/`) — `catalog/urls.py`
- [x] 3.5 Wire catalog.urls + static() media serving in DEBUG — `config/urls.py`

## Phase 4: Templates

- [x] 4.1 Create base layout with HTMX CDN — `catalog/templates/catalog/base.html`
- [x] 4.2 Create full list page — `pages/product_list.html`
- [x] 4.3 Create detail page — `pages/product_detail.html`
- [x] 4.4 Create partials: `_product_grid.html`, `_product_card.html`, `_filters.html`, `_search_bar.html`, `_pagination.html`

## Phase 5: Integration & Edge Cases

- [x] 5.1 [RED] Write HTMX partial response test (no `<html>` wrapper) — `catalog/tests.py`
- [x] 5.2 [RED] Write edge case tests (malformed price, empty brand, non-existent category, missing image) — `catalog/tests.py`
- [x] 5.3 [RED] Write image upload + media serving tests — `catalog/tests.py`
- [x] 5.4 [GREEN] Implement remaining template fallbacks (no-image placeholder, empty state)
- [x] 5.5 Final: `python manage.py test catalog` — all green
