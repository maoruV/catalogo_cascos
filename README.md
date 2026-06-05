# Catálogo de Cascos y Accesorios

Landing page con catálogo de cascos y accesorios para motocicletas. Filtrado en tiempo real, búsqueda por nombre, paginación, y administración completa desde el admin de Django.

## Stack

- **Python** 3.13
- **Django** 6.0.6
- **SQLite** (via ORM)
- **HTMX** 2.0.4 — filtrado en tiempo real (GET-based, sin CSRF)
- **Tailwind CSS** — CDN, diseño responsivo
- **Pillow** 12.2.0 — manejo de imágenes
- **uv** — gestor de dependencias

## Funcionalidades

### Público

- Landing page con grilla de productos paginada (12 por página)
- Búsqueda en tiempo real por nombre (HTMX, debounce 300ms)
- Filtros combinables: categoría, marca, rango de precio
- Página de detalle de producto con imagen y descripción
- Diseño responsivo (1, 2, 3 columnas según viewport)
- Productos inactivos no visibles para el público

### Admin (`/admin/`)

- CRUD completo de productos y categorías
- Subida de imágenes desde el admin
- Filtros por estado (activo/inactivo) y categoría
- Búsqueda por nombre y marca
- Vista de cantidad de productos por categoría

### Modelo de datos

**Categoría**
| Campo | Tipo |
|-------|------|
| nombre | CharField (unique) |

**Producto**
| Campo | Tipo |
|-------|------|
| nombre | CharField |
| marca | CharField |
| precio | DecimalField |
| descripción | TextField (opcional) |
| imagen | ImageField (subible desde admin) |
| activo | BooleanField (default=True) |
| categoría | ForeignKey → Categoría (opcional, SET_NULL) |

## Quick start

```bash
# Clonar
git clone <repo>
cd catalogo_cascos

# Crear entorno y activar
uv venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Instalar dependencias
uv sync

# Migrar base de datos
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Correr servidor de desarrollo
python manage.py runserver
```

Abrir `http://localhost:8000/` para ver el catálogo y `http://localhost:8000/admin/` para el panel de administración.

## Tests

```bash
python manage.py test catalog
```

Actualmente **43 tests** (12 unit + 31 integration) cubriendo modelos, vistas, admin, filtros, paginación, HTMX, subida de imágenes y edge cases.

## Estructura del proyecto

```
catalogo_cascos/
├── catalog/                     # App principal
│   ├── admin.py                 # Configuración del admin
│   ├── models.py                # Product + Category
│   ├── views.py                 # ListView + DetailView con filtros
│   ├── urls.py                  # Rutas del catálogo
│   ├── tests.py                 # 43 tests
│   ├── templates/catalog/
│   │   ├── base.html            # Layout base (Tailwind + HTMX CDN)
│   │   ├── pages/
│   │   │   ├── product_list.html
│   │   │   └── product_detail.html
│   │   └── partials/
│   │       ├── _product_grid.html
│   │       ├── _product_card.html
│   │       ├── _filters.html
│   │       ├── _search_bar.html
│   │       └── _pagination.html
│   └── migrations/
├── config/                      # Configuración de Django
│   ├── settings.py
│   └── urls.py
├── openspec/                    # Artefactos SDD
│   ├── config.yaml
│   ├── specs/                   # Especificaciones fuente
│   └── changes/archive/         # Cambios completados
├── media/                       # Imágenes subidas (en dev)
├── manage.py
├── pyproject.toml
└── README.md
```

## Desarrollo

Este proyecto se desarrolló siguiendo el flujo **SDD (Spec-Driven Development)** con las siguientes fases:

1. **Exploración** — análisis de enfoques (HTMX vs vanilla JS, página dedicada vs modal, etc.)
2. **Propuesta** — definición de alcance, capacidades y riesgos
3. **Especificaciones** — 4 specs con 30 escenarios Given/When/Then
4. **Diseño** — 14 decisiones de arquitectura documentadas
5. **Implementación** — 3 PRs stacked-to-main con Strict TDD (22 tareas)
6. **Verificación** — 43 tests, PASS WITH WARNINGS
7. **Archivo** — specs mergeadas a la fuente de verdad

## Roadmap (ideas para después)

- [ ] Carrito de compras y checkout
- [ ] Slugs / URLs amigables para SEO
- [ ] Cloud storage para imágenes (S3/Cloudinary)
- [ ] Pytest + pytest-django + coverage
- [ ] Ruff (linter + formatter)
- [ ] Deploy con instrucciones para producción
