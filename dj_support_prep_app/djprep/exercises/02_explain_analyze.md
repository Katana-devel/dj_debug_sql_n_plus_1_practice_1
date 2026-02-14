# Exercise 2: EXPLAIN ANALYZE

## Django ORM Refresher

### How Django Generates SQL

Every QuerySet method builds up a SQL query:

```python
Product.objects.filter(price__gt=100).order_by('name')
# Becomes: SELECT * FROM shop_product WHERE price > 100 ORDER BY name
```

You can see the SQL with:
```python
print(queryset.query)
```

### Indexes in Django

Indexes speed up WHERE clauses, ORDER BY, and JOINs. Without an index, PostgreSQL must scan every row (Sequential Scan).

```python
# Add index to a field
class Product(models.Model):
    created_at = models.DateTimeField(db_index=True)

# Or in Meta
class Product(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['status', 'created_at']),
        ]
```

### Creating Index Migrations

```bash
# After modifying models
python manage.py makemigrations
python manage.py migrate
```

---

## Understanding EXPLAIN ANALYZE

EXPLAIN shows how PostgreSQL plans to execute a query.
EXPLAIN ANALYZE actually runs it and shows real timings.

```sql
EXPLAIN ANALYZE SELECT * FROM shop_product WHERE price > 100;
```

Key things to look for:
- **Scan type**: Seq Scan (bad for filtered queries) vs Index Scan (good)
- **Cost**: Estimated work units
- **Rows**: Estimated vs actual row counts
- **Time**: Actual execution time in milliseconds

---

## Your Task

### Part 1: Connect to PostgreSQL

Option A - Django shell:
```python
python manage.py shell

from debug_tools.explain_helper import explain_query
from shop.models import Product, Order
```

Option B - psql directly:
```bash
psql -h localhost -U djuser -d djprep
# Password: djpass
```

### Part 2: Analyze These Queries

Run EXPLAIN ANALYZE on these scenarios and answer the questions:

**Query 1: Products by date**
```python
from django.utils import timezone
from datetime import timedelta

week_ago = timezone.now() - timedelta(days=7)
qs = Product.objects.filter(created_at__gte=week_ago)
explain_query(qs)
```

Questions:
- What scan type is being used?
- How many rows are being scanned vs returned?
- Would an index help here?

**Query 2: Orders by status**
```python
qs = Order.objects.filter(status='pending')
explain_query(qs)
```

Questions:
- What scan type is being used?
- What's the filter condition?
- How selective is this query?

**Query 3: Products with category join**
```python
qs = Product.objects.select_related('category').filter(category__name='Electronics')
explain_query(qs)
```

Questions:
- What type of join is being used?
- Is the join condition using an index?

### Part 3: Add Indexes

Based on your analysis, identify fields that would benefit from indexes.

1. Modify `shop/models.py` to add appropriate indexes
2. Create and run migrations
3. Re-run EXPLAIN ANALYZE to compare

### Part 4: Measure the Difference

For each query you optimized:
- Note the scan type before and after
- Note the execution time before and after
- Calculate the improvement percentage

---

## Key Concepts

### Seq Scan
- Reads every row in the table
- O(n) complexity
- Fine for small tables, problematic for large ones

### Index Scan
- Uses B-tree index to jump to relevant rows
- O(log n) complexity for lookup
- Best for selective queries (returning small % of rows)

### When Indexes Don't Help
- Very small tables
- Queries returning most rows (>10-20%)
- Columns with low cardinality (few unique values)

---

## Hints

<details>
<summary>Hint 1: Which fields need indexes?</summary>
Look at the fields used in WHERE clauses and filter() calls. Those are candidates for indexing.
</details>

<details>
<summary>Hint 2: Checking existing indexes</summary>
You can see existing indexes in psql with: \di shop_*
</details>

<details>
<summary>Hint 3: Index on status field</summary>
The status field has few unique values. Consider whether the selectivity is high enough to benefit from an index.
</details>

---

## Check Solution

When you're done, compare with [solutions/02_explain_analyze_solution.md](solutions/02_explain_analyze_solution.md)
