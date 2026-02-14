# Solution: EXPLAIN ANALYZE

## Analysis Results

### Query 1: Products by date

**Before (no index on created_at)**:
```
Seq Scan on shop_product  (cost=0.00..35.50 rows=100 width=256)
  Filter: (created_at >= '2024-01-01'::timestamp)
  Rows Removed by Filter: 900
  Actual time: 0.015..0.892 rows=100 loops=1
```

The Seq Scan means PostgreSQL is reading every row in the table.

**Fix - Add index to created_at**:
```python
class Product(models.Model):
    # ...
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
```

**After**:
```
Index Scan using shop_product_created_at_idx on shop_product
  Index Cond: (created_at >= '2024-01-01'::timestamp)
  Actual time: 0.025..0.156 rows=100 loops=1
```

---

### Query 2: Orders by status

**Before (no index on status)**:
```
Seq Scan on shop_order  (cost=0.00..18.50 rows=100 width=64)
  Filter: (status = 'pending')
  Rows Removed by Filter: 400
```

**Fix - Add index to status**:
```python
class Order(models.Model):
    # ...
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
```

**After**:
```
Index Scan using shop_order_status_idx on shop_order
  Index Cond: (status = 'pending')
```

**Note**: Status has low cardinality (only 5 values). Index helps because queries typically filter for one specific status, making them selective enough.

---

### Query 3: Products with category join

The join on category_id should already use an index because ForeignKey creates one automatically.

```
Nested Loop  (cost=0.29..16.34 rows=1 width=256)
  ->  Index Scan using shop_category_name_idx on shop_category
        Index Cond: (name = 'Electronics')
  ->  Index Scan using shop_product_category_id on shop_product
        Index Cond: (category_id = shop_category.id)
```

If you see Seq Scan on category, add index to Category.name:
```python
class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True)
```

---

## Updated Models

```python
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)  # Added index


class Order(models.Model):
    STATUS_CHOICES = [...]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)  # Added index
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

---

## Key Takeaways

1. **Seq Scan on filtered queries** = missing index
2. **ForeignKey fields** get indexes automatically
3. **Low cardinality fields** can still benefit from indexes if queries are selective
4. Always **measure before and after** adding indexes
5. **ANALYZE** the table after adding data to update statistics
