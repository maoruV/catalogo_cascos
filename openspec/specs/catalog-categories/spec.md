# Catalog Categories Specification

## Purpose

Define the Category model and its admin CRUD, which serves as a taxonomy for catalog products.

## Requirements

### Requirement: Category model

The system MUST provide a `Category` model with a `name` field (CharField, max 100, unique). The model MUST return `name` as its string representation.

#### Scenario: Happy path — create a category

- GIVEN a unique category name "Casco Integral"
- WHEN a Category with that name is created
- THEN the category is persisted
- AND `str(category)` returns "Casco Integral"

#### Scenario: Edge case — duplicate name rejected

- GIVEN a Category named "Casco Integral" already exists
- WHEN a second Category with the same name is created
- THEN a database integrity error is raised
- AND the duplicate is not persisted

### Requirement: Admin CRUD for Category

The system MUST register `Category` in the Django admin. Admin users MUST be able to create, list, edit, and delete categories. The list view MUST display `name` and the count of related products.

#### Scenario: Happy path — create and view category list

- GIVEN a logged-in admin user
- WHEN the admin creates a Category named "Accesorio"
- THEN the category appears in the admin category list
- AND the product count column shows 0

#### Scenario: Edge case — delete category with products

- GIVEN a Category has 5 related Product instances
- WHEN an admin attempts to delete that category
- THEN the delete confirmation page warns about 5 related products
- AND the admin can choose to delete or cancel

### Requirement: Product-Category relationship

The `Product` model MUST have a nullable `ForeignKey` to `Category` (`on_delete=SET_NULL`). Setting a category to inactive or deleting it MUST NOT cascade-delete products.

#### Scenario: Happy path — product linked to category

- GIVEN a Category exists
- WHEN a Product is created with that category
- THEN `product.category` returns the expected Category instance

#### Scenario: Edge case — category deleted, products preserved

- GIVEN 3 products linked to a Category
- WHEN that Category is deleted
- THEN all 3 products remain in the database with `category=NULL`
