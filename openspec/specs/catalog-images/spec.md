# Catalog Images Specification

## Purpose

Define image upload, storage, and display for Product models via Django's ImageField and local media configuration.

## Requirements

### Requirement: ImageField on Product

The Product model MUST include an `ImageField` named `image` with `upload_to='products/'`. The field MUST be optional (nullable and blank). Uploaded images MUST be validated by Django's ImageField (non-image files MUST be rejected).

#### Scenario: Happy path — upload a valid image

- GIVEN a Django admin or form POST including a valid JPEG file
- WHEN a Product is created with the image field set
- THEN the image is saved under `MEDIA_ROOT/products/<filename>`
- AND `product.image.url` returns a resolvable URL

#### Scenario: Edge case — no image provided

- GIVEN a Product is created without an image
- WHEN the Product is saved
- THEN `product.image` is an empty string
- AND the detail view renders without an image tag (or with a placeholder)

### Requirement: MEDIA_URL and MEDIA_ROOT configuration

The system MUST configure `MEDIA_URL='/media/'` and `MEDIA_ROOT=os.path.join(BASE_DIR, 'media')` in settings. In development (DEBUG=True), static file serving MUST include media files at `/media/`. File access MUST be restricted to `DEBUG=True` only when using `django.conf.urls.static.static()`.

#### Scenario: Happy path — media served in development

- GIVEN `DEBUG=True` and a stored product image at `media/products/helmet.jpg`
- WHEN a browser requests `/media/products/helmet.jpg`
- THEN the image file is served successfully (200)

#### Scenario: Edge case — debug disabled, no media serving

- GIVEN `DEBUG=False`
- WHEN a browser requests `/media/products/helmet.jpg`
- THEN the request returns 404 (not served by Django)

### Requirement: Image display in views

The public list view and detail view MUST render the product image when present. The list view SHOULD display a thumbnail (CSS-max-width or Django template resize). The detail view SHOULD display the full image at its original dimensions.

#### Scenario: Happy path — image shown in detail

- GIVEN a product with an uploaded image
- WHEN a user visits the product detail page
- THEN an `<img>` tag with `src` pointing to the image URL is rendered
- AND the image is displayed

#### Scenario: Edge case — missing image in list

- GIVEN a product without an image
- WHEN the product appears in the list view
- THEN the product card renders without a broken image icon
- AND a CSS fallback placeholder or no image area is shown

### Requirement: Pillow dependency

The project MUST declare `Pillow>=11` as a project dependency in `pyproject.toml`. Django's ImageField MUST be usable without `Pillow` import errors.

#### Scenario: Happy path — Pillow installed

- GIVEN `Pillow` is listed in project dependencies
- WHEN `pip install -e .` or equivalent is run
- THEN Django's ImageField validates and processes images without errors

#### Scenario: Edge case — missing Pillow

- GIVEN `Pillow` is not installed
- WHEN Django attempts to use ImageField
- THEN a `ImproperlyConfigured` exception is raised with a clear message about Pillow
