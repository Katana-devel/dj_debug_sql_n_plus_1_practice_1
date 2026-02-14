# Solution: N+1 Queries

## product_list

**Problem**: Accessing `product.category.name` and `product.created_by.username` in the loop triggers a query for each product.

**Fix**:
```python
def product_list(request):
    products = Product.objects.select_related('category', 'created_by')
    # ... rest of view
```

**Result**: 1 query instead of 1 + 2N queries

---

## order_list

**Problem**: Accessing `order.user.username` in the loop.

**Fix**:
```python
def order_list(request):
    orders = Order.objects.select_related('user')[:50]
    # ... rest of view
```

**Result**: 1 query instead of 1 + N queries

---

## order_detail

**Problem**: Multiple levels of N+1:
1. `order.items.all()` - fetches items
2. `item.product.name` - fetches product for each item
3. `item.product.category.name` - fetches category for each product
4. `order.user.username` - fetches user
5. `order.total` property iterates items again

**Fix**:
```python
from django.db.models import Prefetch
from .models import OrderItem

def order_detail(request, pk):
    order = get_object_or_404(
        Order.objects.select_related('user').prefetch_related(
            Prefetch(
                'items',
                queryset=OrderItem.objects.select_related('product__category')
            )
        ),
        pk=pk
    )
    # ... rest of view
```

**Result**: 2 queries instead of 1 + N + N + N queries

---

## category_products

**Problem**: Accessing `product.created_by.username` in loop.

**Fix**:
```python
def category_products(request, pk):
    category = get_object_or_404(Category, pk=pk)
    products = category.products.select_related('created_by')
    # ... rest of view
```

**Result**: 2 queries instead of 1 + N queries

---

## Key Takeaways

1. **select_related** for ForeignKey/OneToOne (forward relationships)
2. **prefetch_related** for reverse FK and ManyToMany
3. **Prefetch object** when the prefetched queryset needs its own optimizations
4. Watch out for properties that iterate related objects (like `order.total`)
