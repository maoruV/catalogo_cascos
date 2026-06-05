# Catalog Search Specification

## Purpose

Define real-time search and filtering over catalog products via HTMX GET requests with debounced input.

## Requirements

### Requirement: Text search by product name

The system MUST provide a search endpoint (GET `/` with `q` param) that filters active products by name using a case-insensitive containment match. The response MUST be an HTML partial suitable for HTMX swap. The search SHOULD trigger on `keyup` with a 300ms debounce delay.

#### Scenario: Happy path — search finds matching products

- GIVEN active products named "Casco Integral", "Casco Modular", and "Guantes"
- WHEN a user types "Casco" in the search bar
- THEN the partial response contains both "Casco Integral" and "Casco Modular"
- AND "Guantes" is excluded

#### Scenario: Edge case — no matches

- GIVEN no product names contain "Zapatillas"
- WHEN a user types "Zapatillas"
- THEN the partial response contains a "no products found" message
- AND the response has 200 status

### Requirement: Filter by category

The system MUST support filtering by category via GET param `categoria` (category ID). Multiple categories MAY be combined using comma-separated IDs. Results MUST exclude inactive products.

#### Scenario: Happy path — single category filter

- GIVEN products in categories "Integral" (id=1) and "Modular" (id=2)
- WHEN a user visits `/?categoria=1`
- THEN only "Integral" products are displayed

#### Scenario: Edge case — non-existent category

- GIVEN no category with id=999 exists
- WHEN a user visits `/?categoria=999`
- THEN the response shows an empty grid with "no products found"
- AND the response status is 200

### Requirement: Filter by brand

The system MUST support filtering by brand via GET param `marca`. Brand filter MUST use exact case-insensitive match. Results MUST exclude inactive products.

#### Scenario: Happy path — brand filter

- GIVEN products by "Shark" and "AGV"
- WHEN a user visits `/?marca=shark`
- THEN only "Shark" products are shown

#### Scenario: Edge case — empty brand value

- GIVEN `/?marca=` is sent (empty string)
- WHEN the view processes the request
- THEN the brand filter is ignored and all active products are returned

### Requirement: Filter by price range

The system MUST support price range filtering via GET params `precio_min` and `precio_max`. Only active products within the inclusive range MUST be returned. Each parameter SHOULD be optional.

#### Scenario: Happy path — price range

- GIVEN products at prices 100, 200, 300, and 400
- WHEN a user visits `/?precio_min=150&precio_max=350`
- THEN only products at 200 and 300 are returned

#### Scenario: Edge case — malformed price values

- GIVEN `precio_min=abc` is sent
- WHEN the view processes the request
- THEN the malformed filter is silently ignored and all active products are returned
