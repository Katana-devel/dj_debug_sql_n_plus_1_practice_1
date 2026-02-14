# Interview Prep Exercises

This environment is designed to help you practice database debugging skills for Django applications.

## Setup

```bash
# 1. Start PostgreSQL
docker-compose up -d

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations
python manage.py migrate

# 4. Seed sample data
python manage.py seed_data

# 5. Start server
python manage.py runserver
```

## Exercises

Work through these in order:

1. **[N+1 Queries](01_n_plus_one.md)** - Learn to detect and fix N+1 query problems
2. **[EXPLAIN ANALYZE](02_explain_analyze.md)** - Learn to read query plans and add indexes
3. **[Bug Hunt](03_bug_hunt.md)** - Practice diagnosing a slow endpoint

## Available Endpoints

| Endpoint | Description |
|----------|-------------|
| `/shop/products/` | List all products |
| `/shop/products/<id>/` | Product detail |
| `/shop/products/recent/` | Products from last 7 days |
| `/shop/orders/` | List recent orders |
| `/shop/orders/<id>/` | Order detail with items |
| `/shop/orders/dashboard/` | Order dashboard (target for bug hunt) |
| `/shop/categories/<id>/products/` | Products in category |

## Debug Tools

### Console SQL Logging
The middleware logs all queries to the console. Watch for:
- High query counts
- Duplicate queries
- Slow queries (>100ms)

### Django Debug Toolbar
Visit any page in browser to see the toolbar panel with SQL analysis.

### EXPLAIN Helper
```python
python manage.py shell

from debug_tools.explain_helper import explain_query
from shop.models import Product

qs = Product.objects.filter(price__gt=100)
explain_query(qs)
```

## Cheatsheets

Quick reference materials:
- [Django ORM](../cheatsheets/django_orm.md)
- [EXPLAIN ANALYZE](../cheatsheets/explain_analyze.md)

## Solutions

Solutions are in the `solutions/` folder. Try to solve each exercise before checking!
