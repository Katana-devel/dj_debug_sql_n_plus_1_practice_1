# Solution: Bug Hunt

## Issues Found

### Issue 1: N+1 on user
Each `order.user.username` triggers a separate query.

### Issue 2: N+1 on items
Each `order.items.all()` triggers a separate query.

### Issue 3: N+1 on item.product
Each `item.product.name` triggers a separate query.

### Issue 4: order.total triggers more queries
The `total` property iterates `self.items.all()` again, and accesses item.price, causing another round of queries.

### Issue 5: No pagination
`Order.objects.all()` loads every order. With thousands of orders this is a disaster.

### Issue 6: Missing index on status
Filtering by status does a Seq Scan without an index.

---

## The Fix

```python
from django.db.models import Prefetch, Sum, F
from django.core.paginator import Paginator

def order_dashboard(request):
    status = request.GET.get('status', None)
    page = request.GET.get('page', 1)

    orders = Order.objects.select_related('user').prefetch_related(
        Prefetch(
            'items',
            queryset=OrderItem.objects.select_related('product')
        )
    ).annotate(
        calculated_total=Sum(F('items__price') * F('items__quantity'))
    )

    if status:
        orders = orders.filter(status=status)

    orders = orders.order_by('-created_at')

    paginator = Paginator(orders, 20)
    page_obj = paginator.get_page(page)

    data = []
    for order in page_obj:
        items = []
        for item in order.items.all():
            items.append({
                'product': item.product.name,
                'quantity': item.quantity,
            })

        data.append({
            'id': order.id,
            'user': order.user.username,
            'status': order.status,
            'item_count': len(items),
            'items': items,
            'total': str(order.calculated_total or 0),
        })

    return JsonResponse({
        'orders': data,
        'page': page_obj.number,
        'total_pages': paginator.num_pages,
        'total_orders': paginator.count,
    })
```

---

## Model Changes

Add index to status field:

```python
class Order(models.Model):
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True  # Add this
    )
```

Then run:
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Results

| Metric | Before | After |
|--------|--------|-------|
| Query count | 1 + 3N (hundreds) | 3 |
| Response time | 2-5 seconds | < 50ms |
| Memory usage | High (all orders loaded) | Low (20 per page) |

---

## Key Takeaways

1. **Always paginate** list endpoints
2. **Use select_related** for FK accessed in loop
3. **Use prefetch_related with Prefetch** for nested relationships
4. **Use annotate** instead of Python property calculations
5. **Add indexes** on fields used in filters
6. **Profile first** - the middleware showed exactly where queries came from
