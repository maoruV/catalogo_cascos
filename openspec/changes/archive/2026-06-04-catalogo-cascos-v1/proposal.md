# Proposal: Catálogo de Cascos y Accesorios — v1

## Intent

Crear un catálogo público de cascos y accesorios para motocicletas con filtrado en tiempo real, búsqueda por nombre, paginación y administración CRUD desde el admin de Django. Partimos de un proyecto Django 6.0.6 recién inicializado sin ninguna app ni configuración de medios.

## Scope

### In Scope
- App `catalog` única con modelos Product y Category
- Admin CRUD para productos y categorías
- Landing page con grilla de productos, filtros y paginación
- Página dedicada de detalle de producto
- Búsqueda en tiempo real vía HTMX + GET params
- Carga de imágenes (Pillow + MEDIA_ROOT local)
- Tests unitarios e integración para toda la capa nueva

### Out of Scope
- Carrito de compras, checkout, órdenes
- Usuarios, registro, perfiles
- Cloud storage para imágenes
- Configuración de producción (deploy, proxy)
- Slugs / SEO / URLs amigables (postergado)

## Capabilities

> Todos los capabilities son NUEVOS — no existen specs previos.

### New Capabilities
- `catalog-products`: Modelo Product (nombre, marca, precio, descripción, imagen, activo), listado con filtros y paginación, detalle individual, CRUD via admin
- `catalog-categories`: Modelo Category con nombre, CRUD via admin, FK desde Product
- `catalog-search`: Barra de búsqueda + filtros por categoría, marca, rango de precio — todo vía GET + HTMX
- `catalog-images`: ImageField en Product, configuración MEDIA_URL/MEDIA_ROOT, Pillow como dependencia

### Modified Capabilities
- None — proyecto sin capacidades previas

## Approach

Single `catalog` app con modelos Product (FK → Category) y Category. HTMX desde CDN para filtrado en tiempo real con debounce (keyup delay 300ms). Django Paginator con números de página. Vistas basadas en clase (ListView, DetailView). GET params para filtros (sin CSRF). Plantillas separadas en `pages/` y `partials/` para swaps HTMX. Pillow + MEDIA_ROOT local para imágenes. Tests con Django TestCase por requirement de `strict_tdd: true`.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `config/settings.py` | Modified | INSTALLED_APPS, MEDIA_URL, MEDIA_ROOT |
| `config/urls.py` | Modified | Agregar URLs de catalog + media en dev |
| `pyproject.toml` | Modified | Agregar Pillow como dependencia |
| `catalog/` | New | Models, views, admin, urls, templates, tests |
| `openspec/specs/catalog/` | New | Specs de catalog-products, catalog-categories, catalog-search, catalog-images |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Pillow no instalada | High | Agregar a pyproject.toml antes de migrar |
| Media solo sirve en DEBUG | Low (v1) | Documentado; no blocker para desarrollo |
| Sin tests previos | Medium | Escribir tests primero (strict_tdd: true) |

## Rollback Plan

1. Eliminar app `catalog/` y remover de INSTALLED_APPS
2. Revertir MEDIA_URL/MEDIA_ROOT en settings.py
3. Revertir URLs de catalog y media en urls.py
4. Ejecutar `python manage.py migrate catalog zero`
5. Remover Pillow de pyproject.toml si no se usa en otra parte

## Dependencies

- `Pillow` (>=11) — requerido por ImageField de Django

## Success Criteria

- [ ] `python manage.py test catalog` pasa todos los tests
- [ ] Admin permite crear, editar y desactivar productos y categorías
- [ ] Landing page muestra productos paginados con filtros funcionales
- [ ] Búsqueda por nombre filtra en tiempo real (<500ms respuesta)
- [ ] Página de detalle de producto carga correctamente
- [ ] Imágenes se suben desde admin y se muestran en frontend
