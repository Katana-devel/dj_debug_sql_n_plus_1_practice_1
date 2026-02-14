# Exercise 1: N+1 Queries

## Django ORM Refresher

### What is a QuerySet?

A QuerySet represents a collection of objects from your database. The key thing to understand is that QuerySets are **lazy** - they don't actually hit the database until you need the data.

```python
# This doesn't execute any query yet
products = Product.objects.filter(price__gt=100)

# Query executes when you iterate, slice, call len(), etc.
for p in products:
    print(p.name)
```

### ForeignKey Relationships

When you define a ForeignKey, Django creates a relationship between models:

```python
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
```

Accessing `product.category` triggers a database query to fetch the related Category object - unless it's already been fetched.

---

## Understanding N+1

The N+1 query problem occurs when you:
1. Fetch a list of N objects (1 query)
2. Access a related object on each one (N queries)

```python
# 1 query to get products
products = Product.objects.all()

# N queries - one for each product's category
for product in products:
    print(product.category.name)
```

If you have 100 products, this results in 101 queries instead of 1-2.

---

## Your Task

### Part 1: Detect N+1 Problems

1. Start the server: `python manage.py runserver`
2. Open your terminal to see SQL logs
3. Visit these endpoints and count the queries:
   - `http://localhost:8000/shop/products/`
   - `http://localhost:8000/shop/orders/`
   - `http://localhost:8000/shop/orders/1/`

Questions to answer:
- How many queries are being executed?
- What pattern do you see in the duplicate queries?
- Which related models are being fetched repeatedly?

### Part 2: Fix the Problems

Look at `shop/views.py` and modify the querysets to eliminate the N+1 issues.

For each view, determine:
- Which related objects are being accessed in the loop?
- Should you use `select_related()` or `prefetch_related()`?
- Are there nested relationships that need handling?

### Part 3: Verify Your Fixes

After fixing each view:
1. Refresh the endpoint
2. Check the query count in the console
3. Confirm queries are no longer duplicated

---

## Key Concepts

### When to use select_related()
- ForeignKey relationships (forward)
- OneToOneField relationships
- Creates a SQL JOIN

### When to use prefetch_related()
- ManyToMany relationships
- Reverse ForeignKey (accessing `order.items` when OrderItem has FK to Order)
- Uses separate queries, joins in Python

### When to use Prefetch()
- When you need to filter or customize the prefetch query
- When the prefetched queryset itself needs `select_related()`

---

## Hints

<details>
<summary>Hint 1: product_list view</summary>
Look at what attributes you're accessing on each product in the loop.
</details>

<details>
<summary>Hint 2: order_detail view</summary>
There are multiple levels of relationships being accessed. Think about what order.items returns, and what you access on each item.
</details>

<details>
<summary>Hint 3: Nested prefetch</summary>
Sometimes you need to combine select_related inside a Prefetch object to handle nested relationships efficiently.
</details>

---

## Check Solution

When you're done, compare with [solutions/01_n_plus_one_solution.md](solutions/01_n_plus_one_solution.md)
