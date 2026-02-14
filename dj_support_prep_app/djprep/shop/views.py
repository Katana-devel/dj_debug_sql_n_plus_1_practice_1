from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Product, Order, Category


def product_list(request):
    """List all products with basic info."""
    products = Product.objects.all()

    data = []
    for product in products:
        data.append({
            'id': product.id,
            'name': product.name,
            'price': str(product.price),
            'category': product.category.name,
            'created_by': product.created_by.username,
        })

    return JsonResponse({'products': data})


def product_detail(request, pk):
    """Get detailed product info with category breadcrumb."""
    product = get_object_or_404(Product, pk=pk)

    breadcrumb = []
    category = product.category
    while category:
        breadcrumb.insert(0, category.name)
        category = category.parent

    data = {
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': str(product.price),
        'category_breadcrumb': ' > '.join(breadcrumb),
        'created_by': product.created_by.username,
    }

    return JsonResponse(data)


def order_list(request):
    """List recent orders."""
    orders = Order.objects.all()[:50]

    data = []
    for order in orders:
        data.append({
            'id': order.id,
            'user': order.user.username,
            'status': order.status,
            'created_at': order.created_at.isoformat(),
        })

    return JsonResponse({'orders': data})


def order_detail(request, pk):
    """Get order details with all items."""
    order = get_object_or_404(Order, pk=pk)

    items_data = []
    for item in order.items.all():
        items_data.append({
            'product': item.product.name,
            'category': item.product.category.name,
            'quantity': item.quantity,
            'price': str(item.price),
            'subtotal': str(item.subtotal),
        })

    data = {
        'id': order.id,
        'user': order.user.username,
        'status': order.status,
        'items': items_data,
        'total': str(order.total),
    }

    return JsonResponse(data)


def order_dashboard(request):
    """Dashboard showing all orders with their items."""
    status = request.GET.get('status', None)

    orders = Order.objects.all()

    if status:
        orders = orders.filter(status=status)

    data = []
    for order in orders:
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
            'total': str(order.total),
        })

    return JsonResponse({'orders': data})


def category_products(request, pk):
    """Get all products in a category."""
    category = get_object_or_404(Category, pk=pk)
    products = category.products.all()

    data = []
    for product in products:
        data.append({
            'id': product.id,
            'name': product.name,
            'price': str(product.price),
            'created_by': product.created_by.username,
        })

    return JsonResponse({
        'category': category.name,
        'products': data
    })


def products_by_date(request):
    """Get products created in the last 7 days."""
    from django.utils import timezone
    from datetime import timedelta

    week_ago = timezone.now() - timedelta(days=7)
    products = Product.objects.filter(created_at__gte=week_ago)

    data = []
    for product in products:
        data.append({
            'id': product.id,
            'name': product.name,
            'created_at': product.created_at.isoformat(),
        })

    return JsonResponse({'products': data})
