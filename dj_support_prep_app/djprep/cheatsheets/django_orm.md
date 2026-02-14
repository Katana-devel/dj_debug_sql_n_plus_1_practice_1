# Django ORM Quick Reference

## QuerySet Basics

```python
# QuerySets are lazy - no DB hit until evaluated
qs = Product.objects.all()  # No query yet
list(qs)  # Query executes here

# Evaluation triggers:
# - Iteration (for item in qs)
# - Slicing with step (qs[::2])
# - len(), list(), bool()
# - repr(), str()
```

## select_related()

Follows ForeignKey/OneToOne relationships in a single query using SQL JOIN.

```python
# Without - 1 query per product's category
for p in Product.objects.all():
    print(p.category.name)  # Each access = new query

# With - single query with JOIN
for p in Product.objects.select_related('category'):
    print(p.category.name)  # No additional queries

# Chain multiple relations
Product.objects.select_related('category', 'created_by')

# Follow nested relations
Product.objects.select_related('category__parent')
```

## prefetch_related()

For ManyToMany and reverse ForeignKey. Uses separate queries, joins in Python.

```python
# Fetches related items in a separate query
Order.objects.prefetch_related('items')

# Nested prefetch
Order.objects.prefetch_related('items__product')
```

## Prefetch Object

Fine-grained control over prefetch queries.

```python
from django.db.models import Prefetch

# Filter prefetched items
Order.objects.prefetch_related(
    Prefetch('items', queryset=OrderItem.objects.filter(quantity__gte=2))
)

# Combine with select_related in prefetch
Order.objects.prefetch_related(
    Prefetch(
        'items',
        queryset=OrderItem.objects.select_related('product__category')
    )
)

# Custom attribute name
Order.objects.prefetch_related(
    Prefetch('items', queryset=OrderItem.objects.filter(quantity__gte=5), to_attr='bulk_items')
)
```

## only() and defer()

Control which fields are loaded.

```python
# Only load specific fields
Product.objects.only('id', 'name', 'price')

# Load everything except specified fields
Product.objects.defer('description')  # Skip large text field

# Accessing deferred field triggers another query!
p = Product.objects.defer('description').first()
p.description  # New query here
```

## values() and values_list()

Return dictionaries or tuples instead of model instances.

```python
# Dict per row
Product.objects.values('id', 'name')
# [{'id': 1, 'name': 'Phone'}, ...]

# Tuples
Product.objects.values_list('id', 'name')
# [(1, 'Phone'), ...]

# Single values as flat list
Product.objects.values_list('name', flat=True)
# ['Phone', 'Laptop', ...]
```

## Aggregation

```python
from django.db.models import Count, Sum, Avg, Max, Min

# Single aggregate
Product.objects.aggregate(avg_price=Avg('price'))
# {'avg_price': Decimal('123.45')}

# Multiple
Product.objects.aggregate(
    total=Count('id'),
    avg_price=Avg('price'),
    max_price=Max('price')
)
```

## Annotation

Add computed fields to each object.

```python
from django.db.models import Count, Sum, F

# Count related items
orders = Order.objects.annotate(item_count=Count('items'))
orders[0].item_count  # Accessing computed field

# Sum with related field
orders = Order.objects.annotate(
    total=Sum(F('items__price') * F('items__quantity'))
)

# Filter on annotation
Order.objects.annotate(
    item_count=Count('items')
).filter(item_count__gte=3)
```

## Subqueries

```python
from django.db.models import OuterRef, Subquery

# Get latest order date for each user
latest_order = Order.objects.filter(
    user=OuterRef('pk')
).order_by('-created_at').values('created_at')[:1]

User.objects.annotate(
    last_order_date=Subquery(latest_order)
)
```

## Common Patterns

### Avoid N+1 with nested relations
```python
# Bad: 1 + N + N*M queries
for order in Order.objects.all():
    for item in order.items.all():
        print(item.product.name)

# Good: 2 queries total
orders = Order.objects.prefetch_related(
    Prefetch('items', queryset=OrderItem.objects.select_related('product'))
)
for order in orders:
    for item in order.items.all():
        print(item.product.name)
```

### Exists check
```python
# Bad: fetches all rows
if Product.objects.filter(category=cat):
    ...

# Good: stops at first match
if Product.objects.filter(category=cat).exists():
    ...
```

### Count vs len
```python
# Bad: loads all objects
len(Product.objects.all())

# Good: SELECT COUNT(*)
Product.objects.count()
```

### Bulk operations
```python
# Create many at once
Product.objects.bulk_create([
    Product(name='A', price=10),
    Product(name='B', price=20),
])

# Update many at once
Product.objects.filter(category=cat).update(price=F('price') * 1.1)
```

## Debugging Queries

```python
# Print SQL for a queryset
print(queryset.query)

# Get SQL with params
sql, params = queryset.query.sql_with_params()

# In Django shell with django-extensions
# python manage.py shell_plus --print-sql
```
