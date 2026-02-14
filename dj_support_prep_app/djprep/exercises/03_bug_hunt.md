# Exercise 3: Bug Hunt

## The Scenario

You receive a support ticket:

> **Subject: Order dashboard extremely slow**
>
> Hi,
>
> Our order dashboard page is taking forever to load. It was fine when we launched but now with more orders it's unusable. Customers are complaining they can't check their order status.
>
> The endpoint is `/shop/orders/dashboard/`
>
> Can you investigate and fix it ASAP?
>
> Thanks,
> Product Team

---

## Your Task

### Step 1: Reproduce the Problem

1. Make sure you have sample data: `python manage.py seed_data`
2. Start the server: `python manage.py runserver`
3. Visit: `http://localhost:8000/shop/orders/dashboard/`
4. Observe the response time and console output

### Step 2: Diagnose

Using the tools available to you:
- Console SQL logging
- Django Debug Toolbar
- `explain_query()` helper
- Code inspection

Find ALL performance issues in the `order_dashboard` view.

Document each issue you find:
- What is the problem?
- Why does it hurt performance?
- How would you fix it?

### Step 3: Fix the Issues

Modify `shop/views.py` to fix each problem you identified.

### Step 4: Verify

After fixing:
- What's the new query count?
- What's the new response time?
- Try filtering with `?status=pending` - is it fast?

---

## Investigation Checklist

Use this checklist to guide your investigation:

- [ ] How many SQL queries are executed?
- [ ] Are there duplicate queries?
- [ ] Are there sequential scans on large tables?
- [ ] Is there any pagination?
- [ ] What data is being loaded that isn't needed?
- [ ] Are related objects fetched efficiently?

---

## Hints

Only reveal these if you're stuck. Try to find issues on your own first.

<details>
<summary>Hint 1</summary>
Look at how order.user is accessed for each order.
</details>

<details>
<summary>Hint 2</summary>
Look at the nested loop iterating over order.items.
</details>

<details>
<summary>Hint 3</summary>
What happens when you filter by status? Is there an index?
</details>

<details>
<summary>Hint 4</summary>
The view returns ALL orders. What happens when you have thousands?
</details>

<details>
<summary>Hint 5</summary>
Look at the order.total property. What queries does it trigger?
</details>

---

## Success Criteria

Your fix is successful when:
- Query count is reduced by 90%+
- Response time is under 100ms for reasonable data sizes
- The endpoint handles pagination
- Status filtering uses an index

---

## Check Solution

When you're done, compare with [solutions/03_bug_hunt_solution.md](solutions/03_bug_hunt_solution.md)
