# Catalog Products Specification

## Purpose

Define the Product model and its public views (list with filtering/pagination and detail), plus admin CRUD.

## Requirements

### Requirement: Product model fields

The system MUST provide a `Product` model with the following fields: `name` (CharField, max 200), `brand` (CharField, max 100), `price` (DecimalField, max 10 digits, 2 decimal places), `description` (TextField, optional), `image` (ImageField, optional), `active` (BooleanField, default True), and `category` (ForeignKey to `Category`, nullable).

#### Scenario: Happy path — create a full product

- GIVEN a valid `Category` exists
- WHEN a Product is created with name, brand, price, description, image, active=True, and category set
- THEN the Product is persisted with all fields correctly stored
- AND the product appears in the default queryset

#### Scenario: Edge case — optional fields omitted

- GIVEN no category and no image are provided
- WHEN a Product is created with only name, brand, and price
- THEN the Product is saved successfully with `category=NULL`, `image=''`, `active=True`, and `description=''`

### Requirement: Product list view with filtering and pagination

The system MUST provide a public list view at `/` that displays active products paginated (12 per page). The view SHOULD accept GET parameters `categoria`, `marca`, `precio_min`, and `precio_max` to filter results. Filtered results MUST only include active products.

#### Scenario: Happy path — list shows active products paginated

- GIVEN 15 active products exist
- WHEN a user visits `/`
- THEN the first 12 products are displayed
- AND pagination controls for page 2 are shown

#### Scenario: Edge case — filter with no matches

- GIVEN no active products for the given `marca` filter
- WHEN a user visits `/?marca=UnknownBrand`
- THEN the response shows an empty grid and a "no products found" message

### Requirement: Product detail view

The system MUST provide a public detail view at `/<pk>/` displaying name, brand, price, description, image, and category for a single active product. Inactive products MUST return 404.

#### Scenario: Happy path — active product loads

- GIVEN an active product with pk=5 exists
- WHEN a user visits `/5/`
- THEN the page shows the product's name, brand, price, description, category, and image
- AND the response status is 200

#### Scenario: Edge case — inactive product returns 404

- GIVEN a product with pk=3 has `active=False`
- WHEN a user visits `/3/`
- THEN the response status is 404

### Requirement: Admin CRUD for Product

The system MUST register `Product` in the Django admin with list display columns for name, brand, price, active, and category. Admin users MUST be able to create, edit, delete, and toggle `active` on products.

#### Scenario: Happy path — create product via admin

- GIVEN a logged-in admin user
- WHEN the admin creates a Product with all fields filled
- THEN the product is saved and appears in the admin list view

#### Scenario: Edge case — deactivate via admin

- GIVEN an active product exists
- WHEN an admin sets `active=False` and saves
- THEN the product no longer appears in the public list view
- AND it still appears in the admin list
