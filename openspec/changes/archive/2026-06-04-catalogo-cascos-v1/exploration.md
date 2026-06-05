## Exploration: Landing page — catálogo de cascos y accesorios para motocicletas

### Current State

Fresh Django 6.0.6 project created via `django-admin startproject`. Only the `config/` package exists with default settings:

- **INSTALLED_APPS**: Only Django contrib apps (admin, auth, contenttypes, sessions, messages, staticfiles)
- **Templates**: `DIRS` is empty; `APP_DIRS` is `True` — no template directories configured
- **Static files**: Only `STATIC_URL = 'static/'` — no `STATICFILES_DIRS`, no `STATIC_ROOT`
- **Media files**: No `MEDIA_URL` or `MEDIA_ROOT` configured — image uploads not possible yet
- **URLs**: Only `path('admin/', admin.site.urls)` — no public-facing routes
- **DB**: SQLite via ORM, `db.sqlite3` already created (migrations were run)
- **Package mgr**: `uv`, only dependency is `django>=6.0.6`
- **No apps created**: No custom models, views, or templates exist

### Affected Areas

- `config/settings.py` — Must add `MEDIA_URL`, `MEDIA_ROOT`, `INSTALLED_APPS` entry for new app, template dirs, and STATICFILES_DIRS
- `config/urls.py` — Must add public URL patterns for the catalog app and media file serving in development
- `pyproject.toml` — Must add `Pillow` dependency for image fields
- New app `catalog/` — The core of the change: models, views, admin, templates, template tags
- `openspec/specs/catalog/spec.md` — Future delta spec for this domain

### Approaches

#### 1. App structure: single `catalog` app vs multiple apps

**Approach 1A: Single app (`catalog`)**

- **Pros**:
  - Everything in one place (models, views, admin, templates) — simple navigation
  - No circular import risk between sibling apps
  - Matches the scope: one domain, one entity type (products)
  - Easier to reason about for a v1
- **Cons**:
  - If the domain grows significantly (e.g., brands table, category tree, orders, inventory), the single app becomes a monolith within the monolith
- **Effort**: Low

**Approach 1B: Multiple apps (e.g., `products`, `categories`, `catalog`)**

- **Pros**:
  - Clear separation of concerns from day one
  - Easier to extract microservices later
- **Cons**:
  - Over-engineering for a single-entity catalog
  - Creates unnecessary import chains and management overhead
  - Django admin registration becomes scattered
- **Effort**: Medium

**Recommendation**: **Single app (`catalog`)**. Domain scope is small: one model with 8 fields. Premature splitting adds ceremony without benefit. Can be refactored later if the domain expands.

---

#### 2. Image uploads: Media configuration

**Approach 2A: Local filesystem (standard Django)**

- **Pros**:
  - Built into Django, zero external services
  - `ImageField` + `Pillow` + `MEDIA_ROOT/MEDIA_URL` is the documented path
  - Works with admin out of the box
- **Cons**:
  - Not suitable for production at scale (no CDN, single server storage)
  - Requires manual backup strategy for uploaded files
- **Effort**: Low

**Approach 2B: Cloud storage (S3/Cloudinary) from day one**

- **Pros**: Production-ready, CDN-backed, scales horizontally
- **Cons**:
  - Adds complexity (django-storages, credentials, bucket config)
  - Overkill for a v1 catalog
  - Adds cost and setup friction
- **Effort**: High

**Recommendation**: **Local filesystem**. Standard MEDIA_URL/MEDIA_ROOT + Pillow. This is v1, the user wants to get it running. Cloud storage can be swapped in later via `django-storages` without changing the model.

---

#### 3. Real-time filtering & search: HTMX vs Vanilla JS vs Alpine

**Approach 3A: HTMX (hypermedia-driven)**

- **Pros**:
  - Minimal JS — filtering becomes HTML attribute annotations (`hx-get`, `hx-trigger`, `hx-target`, `hx-swap`)
  - Built-in debounce via `hx-trigger="keyup delay:300ms"`
  - Works naturally with Django templates (returns HTML partials, not JSON)
  - No API endpoints needed — just the same view with `request.htmx` check
  - Trivial to add: one `<script>` tag from CDN (already using CDN for Tailwind)
  - Handles the pagination + filter + search combo cleanly (all trigger the same partial swap)
- **Cons**:
  - Another CDN dependency (though small — ~14KB minified)
  - Requires server round-trip for every interaction (but so do the alternatives with a Django backend)
- **Effort**: Low

**Approach 3B: Vanilla JS + Fetch API**

- **Pros**: Zero dependencies, full control
- **Cons**:
  - Must manually implement debounce, partial DOM replacement, error handling
  - Must build and manage the API endpoint (JSON view + client-side rendering)
  - More lines of JS to write and maintain
  - Duplicates template logic in JS for rendering product cards
- **Effort**: Medium

**Approach 3C: Alpine.js**

- **Pros**: Reactive state management, can do client-side filtering for small datasets
- **Cons**:
  - For server-side pagination (which we need for performance), still requires fetch requests
  - Adds more weight than HTMX for this use case
  - Overkill — the filtering is form-based, not a complex reactive UI
- **Effort**: Medium

**Recommendation**: **HTMX**. It matches the use case perfectly: real-time filtering and pagination with a Django backend, using HTML partials. The user is already using CDN for Tailwind, so adding HTMX from CDN is consistent. The pattern is well-documented and battle-tested.

---

#### 4. Template hierarchy

**Recommended structure**:

```
catalog/
  templates/
    catalog/
      base.html                 <- Base layout (Tailwind + HTMX CDN, nav, footer)
      home.html                 <- Landing page (extends base)
      product_detail.html       <- Product detail page (extends base)
  templates/
    catalog/partials/
      product_grid.html         <- Product card grid (for HTMX swap)
      product_card.html         <- Individual product card
      pagination.html           <- Paginator controls
      filters.html              <- Filter form with HTMX triggers
      search_bar.html           <- Search input with HTMX triggers
```

**Rationale**:
- `APP_DIRS: True` means Django finds `catalog/templates/catalog/` automatically
- Partials folder separates reusable HTMX fragments from full pages
- Each partial can be independently swapped via HTMX

**Effort**: Low

---

#### 5. Product detail: Modal vs dedicated page

**Approach 5A: Dedicated page with HTMX enhancement**

- **Pros**:
  - Clean, shareable, bookmarkable URLs (`/productos/1/casco-integral-x/`)
  - Works without JavaScript (progressive enhancement)
  - Simpler to implement — standard Django detail view
  - HTMX can optionally load it in-page via `hx-get` and `hx-target`
  - Better for accessibility (screen readers, keyboard navigation)
- **Cons**:
  - Full page navigation for direct visits (still fast with Django's caching)
- **Effort**: Low

**Approach 5B: Modal overlay**

- **Pros**:
  - Keeps user on the same page
  - Feels more "app-like"
- **Cons**:
  - URL doesn't reflect the current view (unless using History API)
  - Cannot share or bookmark individual products easily
  - Modal accessibility is notoriously tricky (focus trapping, scroll locking, screen reader announcements)
  - More JS complexity for modal show/hide
  - HTML partial must be designed to work both standalone and in a modal
- **Effort**: Medium

**Recommendation**: **Dedicated page** as the primary. Add HTMX-powered quick-view on the listing page if desired later. Shareable URLs and zero-JS fallback are worth the trade-off.

---

#### 6. Pagination strategy

**Standard Django Paginator**

- The `Paginator` class in `django.core.paginator` handles slicing querysets by page
- HTMX loads subsequent pages via `hx-get="?page=2"` with `hx-target="#product-grid"` and `hx-swap="outerHTML"`
- Filter state is preserved by including current filter params in the pagination URL
- Typical page size: 12–20 products (grid-friendly)

| Pattern | Pros | Cons |
|---------|------|------|
| Page numbers | Users know where they are; links are crawlable | More clicks to reach deep pages |
| Infinite scroll | Feels seamless | Bad for footer discovery; hard to return to a position; breaks paginated URL state |
| Load more button | User-initiated; works with HTMX naturally | Extra click for each batch |

**Recommendation**: **Page numbers** for v1. Simple, predictable, accessible, and works with HTMX out of the box. The pagination partial includes page links and "Previous/Next". Each link carries the current filter/search state as query params.

**Effort**: Low

---

#### 7. Category field: CharField with choices vs ForeignKey

**Approach 7A: CharField with choices**

- **Pros**: Simple, no extra table, no migrations complexity
- **Cons**: Changing categories requires a migration; cannot add metadata to categories (description, slug, image)
- **Effort**: Low

**Approach 7B: ForeignKey to Category model**

- **Pros**: Flexible, extensible, can add category images/descriptions later, admin can manage categories
- **Cons**: Slightly more setup (model, admin, fixture for seed data)
- **Effort**: Low-Medium

**Recommendation**: **ForeignKey to Category model**. Categories are a natural entity in a catalog (integral, modular, abierto, accesorio, etc.) and managing them in the admin is better than hardcoding choices. The overhead is minimal: one extra model, one extra admin registration. This is a design choice that's cheap to make now and expensive to retrofit later.

---

### Recommendation

| Area | Decision | Rationale |
|------|----------|-----------|
| App structure | Single `catalog` app | Scope fits one app; refactor later if needed |
| Images | Local filesystem (MEDIA_URL/MEDIA_ROOT + Pillow) | v1 simplicity; swap to cloud later |
| Real-time filtering | **HTMX** (CDN) | Natural fit for Django templates; minimal JS; handles debounce natively |
| Templates | `catalog/templates/catalog/{pages,partials}/` | Standard Django layout with fragment separation |
| Product detail | **Dedicated page** (with HTMX enhancement) | Shareable URLs, accessible, simpler |
| Pagination | **Page numbers** via Django Paginator + HTMX swaps | Predictable, crawlable, HTMX-friendly |
| Categories | **ForeignKey to Category model** | Cheaper now than later; admin-manageable |

### Risks

- **Pillow not installed**: `ImageField` requires Pillow which is not in `pyproject.toml`. Must add before running migrations.
- **Media serving in production**: The `+ static()` helper only works in DEBUG mode. A production deployment will need a proper static/media strategy (whitenoise for static, separate media server or CDN). Not a v1 blocker.
- **HTMX + CSRF**: POST-based filters need CSRF token handling. HTMX handles this via `hx-headers` or including `{% csrf_token %}` in the form. GET-based filtering (recommended) avoids this entirely — filters are query params, no CSRF needed.
- **Template dirs not configured**: `APP_DIRS: True` means Django will find `catalog/templates/` automatically — no `DIRS` change needed for app templates. But if we want a project-level `templates/` dir with a `base.html`, we need to add it to `DIRS`.
- **No tests exist**: Will need to write tests from scratch for models, views, admin, and HTMX behavior. The `config.yaml` specifies `strict_tdd: true`.

### Ready for Proposal

**Yes**. The exploration is complete. The orchestrator should proceed to **sdd-propose** with these findings.

Key points to carry forward:
- Single `catalog` app
- HTMX for real-time filtering
- Dedicated product detail page
- Django Paginator with page numbers
- Category as a model (ForeignKey)
- Pillow + local media setup for images
- All dependencies (HTMX CDN, Tailwind CDN, Pillow)
