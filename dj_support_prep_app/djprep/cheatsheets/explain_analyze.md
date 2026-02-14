# PostgreSQL EXPLAIN ANALYZE Cheatsheet

## Basic Usage

```sql
-- Plan only (estimates)
EXPLAIN SELECT * FROM shop_product WHERE price > 100;

-- Plan + actual execution (real numbers)
EXPLAIN ANALYZE SELECT * FROM shop_product WHERE price > 100;

-- More details
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) SELECT ...
```

## Reading the Output

```
Seq Scan on shop_product  (cost=0.00..25.00 rows=500 width=128) (actual time=0.015..0.234 rows=423 loops=1)
```

| Part | Meaning |
|------|---------|
| `Seq Scan` | Scan type (how data is accessed) |
| `cost=0.00..25.00` | Startup cost..total cost (arbitrary units) |
| `rows=500` | Estimated rows returned |
| `width=128` | Estimated avg row size in bytes |
| `actual time=0.015..0.234` | Startup time..total time in ms |
| `rows=423` | Actual rows returned |
| `loops=1` | Times this node was executed |

## Scan Types

### Sequential Scan (Seq Scan)
- Reads entire table row by row
- Fine for small tables
- Red flag for large tables with WHERE clause

```
Seq Scan on shop_product
  Filter: (price > 100)
```

### Index Scan
- Uses index to find rows, then fetches from table
- Good for selective queries

```
Index Scan using shop_product_category_id on shop_product
  Index Cond: (category_id = 5)
```

### Index Only Scan
- All needed data is in the index
- Fastest option

```
Index Only Scan using shop_product_price_idx on shop_product
  Index Cond: (price > 100)
```

### Bitmap Scans
- Bitmap Index Scan + Bitmap Heap Scan
- Good for medium selectivity

```
Bitmap Heap Scan on shop_product
  Recheck Cond: (price > 100)
  ->  Bitmap Index Scan on shop_product_price_idx
        Index Cond: (price > 100)
```

## Join Types

### Nested Loop
- For each row in outer, scan inner
- Good for small datasets or indexed inner

### Hash Join
- Build hash table from one side
- Good for larger datasets

### Merge Join
- Both sides sorted, merge together
- Good when data already sorted

## Red Flags

| Issue | Sign | Fix |
|-------|------|-----|
| Missing index | `Seq Scan` on large table with filter | Add index |
| Bad estimate | `rows=1000` but `actual rows=1` | ANALYZE table |
| High loops | `loops=10000` | Optimize join or add index |
| Slow sort | `Sort Method: external merge` | Add index, increase work_mem |

## Adding Indexes in Django

```python
# On field definition
class Product(models.Model):
    created_at = models.DateTimeField(db_index=True)
    status = models.CharField(max_length=20, db_index=True)

# In Meta class
class Product(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['category', 'price']),
        ]
```

## Migration for Adding Index

```bash
python manage.py makemigrations
python manage.py migrate
```

Generated migration:
```python
migrations.AddIndex(
    model_name='product',
    index=models.Index(fields=['created_at'], name='shop_produc_created_abc123'),
),
```

## Cost Formula

```
cost = (disk pages read) * seq_page_cost
     + (rows scanned) * cpu_tuple_cost
     + (index entries) * cpu_index_tuple_cost
```

Default costs:
- `seq_page_cost = 1.0`
- `random_page_cost = 4.0` (index access is random)
- `cpu_tuple_cost = 0.01`

## Useful PostgreSQL Commands

```sql
-- Table statistics
SELECT relname, n_live_tup, n_dead_tup
FROM pg_stat_user_tables;

-- Index usage
SELECT indexrelname, idx_scan, idx_tup_read
FROM pg_stat_user_indexes
WHERE schemaname = 'public';

-- Unused indexes
SELECT indexrelname
FROM pg_stat_user_indexes
WHERE idx_scan = 0;

-- Update statistics
ANALYZE shop_product;

-- Table size
SELECT pg_size_pretty(pg_total_relation_size('shop_product'));
```

## Django Shell Helper

```python
from debug_tools.explain_helper import explain_query
from shop.models import Product

qs = Product.objects.filter(price__gt=100)
explain_query(qs)
```
